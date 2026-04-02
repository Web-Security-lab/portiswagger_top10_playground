const express = require('express');
const path = require('path');
const { PrismaClient } = require('@prisma/client');
const { execSync } = require('child_process');

const prisma = new PrismaClient();
const app = express();
const PORT = process.env.PORT || 8080;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

async function ensureSeeded() {
  execSync('npx prisma db push --accept-data-loss', { stdio: 'inherit', cwd: __dirname });
  const count = await prisma.user.count();
  if (count > 0) return;
  console.log('[*] database empty, seeding...');
  execSync('node prisma/seed.js', { stdio: 'inherit', cwd: __dirname });
}

async function getDashboardStats() {
  const employeeCount = await prisma.user.count();
  const departmentCount = (await prisma.user.findMany({ distinct: ['department'], select: { department: true } })).length;
  const locationCount = (await prisma.user.findMany({ distinct: ['location'], select: { location: true } })).length;
  const departments = (await prisma.user.findMany({
    distinct: ['department'],
    select: { department: true },
    orderBy: { department: 'asc' }
  })).map((row) => row.department);
  const locations = (await prisma.user.findMany({
    distinct: ['location'],
    select: { location: true },
    orderBy: { location: 'asc' }
  })).map((row) => row.location);

  return { employeeCount, departmentCount, locationCount, departments, locations };
}

app.get('/', async (req, res) => {
  await ensureSeeded();
  const stats = await getDashboardStats();
  res.render('index', stats);
});

app.get('/api/meta', async (req, res) => {
  await ensureSeeded();
  const stats = await getDashboardStats();
  res.json(stats);
});

app.get('/api/users', async (req, res) => {
  await ensureSeeded();

  const {
    field = 'username',
    op = 'contains',
    value = '',
    department,
    location
  } = req.query;

  try {
    const where = {
      [field]: {
        [op]: value
      }
    };

    if (department) where.department = department;
    if (location) where.location = location;

    const users = await prisma.user.findMany({
      where,
      orderBy: [{ department: 'asc' }, { full_name: 'asc' }],
      select: {
        employee_id: true,
        username: true,
        email: true,
        full_name: true,
        title: true,
        department: true,
        location: true,
        phone_ext: true,
        role: true
      }
    });

    res.json({
      total: users.length,
      items: users
    });
  } catch (err) {
    res.status(400).json({
      error: 'invalid query'
    });
  }
});

app.get('/api/users/:username', async (req, res) => {
  await ensureSeeded();

  try {
    const user = await prisma.user.findUnique({
      where: { username: req.params.username },
      select: {
        employee_id: true,
        username: true,
        email: true,
        full_name: true,
        title: true,
        department: true,
        location: true,
        phone_ext: true,
        role: true
      }
    });

    if (!user) {
      return res.status(404).json({ error: 'user not found' });
    }

    res.json(user);
  } catch (err) {
    res.status(400).json({ error: 'invalid request' });
  }
});

app.get('/health', async (req, res) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ ok: false });
  }
});

app.listen(PORT, async () => {
  await ensureSeeded();
  console.log(`[+] vulnerable app listening on http://0.0.0.0:${PORT}`);
});
