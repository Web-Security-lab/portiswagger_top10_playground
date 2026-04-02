const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function fetchInternalFlag() {
  const url = process.env.INTERNAL_FLAG_URL || 'http://internal-note:5000/flag';
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch internal flag: ${res.status}`);
  }
  const data = await res.json();
  if (!data || typeof data.flag !== 'string') {
    throw new Error('Internal service returned invalid flag data');
  }
  return data.flag;
}

async function main() {
  const existing = await prisma.user.count();
  if (existing > 0) {
    console.log('[+] users already seeded');
    return;
  }

  const flag = await fetchInternalFlag();

  await prisma.user.createMany({
    data: [
      {
        employee_id: 'ACM-0001',
        username: 'admin',
        email: 'admin@corp.local',
        full_name: 'Avery Morgan',
        title: 'Director of Platform Operations',
        department: 'Operations',
        location: 'Seoul HQ',
        phone_ext: '1001',
        role: 'admin',
        reset_token: 'adm-reset-001',
        secret_note: flag
      },
      {
        employee_id: 'ACM-1023',
        username: 'alex',
        email: 'alex@corp.local',
        full_name: 'Alex Carter',
        title: 'Customer Support Specialist',
        department: 'Support',
        location: 'Seoul HQ',
        phone_ext: '2241',
        role: 'user',
        reset_token: 'reset-alex-42',
        secret_note: 'team lunch on friday'
      },
      {
        employee_id: 'ACM-1031',
        username: 'jina',
        email: 'jina@corp.local',
        full_name: 'Jina Park',
        title: 'Office Coordinator',
        department: 'Administration',
        location: 'Seoul HQ',
        phone_ext: '1172',
        role: 'user',
        reset_token: 'reset-jina-77',
        secret_note: 'parking spot B12'
      },
      {
        employee_id: 'ACM-1048',
        username: 'mike',
        email: 'mike@corp.local',
        full_name: 'Michael Reed',
        title: 'IT Support Engineer',
        department: 'IT',
        location: 'Busan Office',
        phone_ext: '3124',
        role: 'user',
        reset_token: 'reset-mike-11',
        secret_note: 'printer toner request'
      },
      {
        employee_id: 'ACM-1060',
        username: 'sora',
        email: 'sora@corp.local',
        full_name: 'Sora Kim',
        title: 'Business Analyst',
        department: 'Strategy',
        location: 'Seoul HQ',
        phone_ext: '2055',
        role: 'user',
        reset_token: 'reset-sora-92',
        secret_note: 'draft budget memo'
      },
      {
        employee_id: 'ACM-1074',
        username: 'hannah',
        email: 'hannah@corp.local',
        full_name: 'Hannah Choi',
        title: 'HR Manager',
        department: 'HR',
        location: 'Seoul HQ',
        phone_ext: '1450',
        role: 'hr',
        reset_token: 'reset-hannah-03',
        secret_note: 'onboarding slides v2 ready'
      },
      {
        employee_id: 'ACM-1088',
        username: 'david',
        email: 'david@corp.local',
        full_name: 'David Lee',
        title: 'Finance Controller',
        department: 'Finance',
        location: 'Seoul HQ',
        phone_ext: '1620',
        role: 'finance',
        reset_token: 'reset-david-18',
        secret_note: 'expense export pending'
      },
      {
        employee_id: 'ACM-1091',
        username: 'nina',
        email: 'nina@corp.local',
        full_name: 'Nina Kwon',
        title: 'Facilities Assistant',
        department: 'Operations',
        location: 'Incheon Warehouse',
        phone_ext: '4113',
        role: 'user',
        reset_token: 'reset-nina-64',
        secret_note: 'badge replacement submitted'
      },
      {
        employee_id: 'ACM-1097',
        username: 'kevin',
        email: 'kevin@corp.local',
        full_name: 'Kevin Jung',
        title: 'Support Team Lead',
        department: 'Support',
        location: 'Seoul HQ',
        phone_ext: '2260',
        role: 'support',
        reset_token: 'reset-kevin-25',
        secret_note: 'night shift handoff checked'
      },
      {
        employee_id: 'ACM-1104',
        username: 'yuna',
        email: 'yuna@corp.local',
        full_name: 'Yuna Han',
        title: 'Marketing Manager',
        department: 'Marketing',
        location: 'Seoul HQ',
        phone_ext: '1880',
        role: 'marketing',
        reset_token: 'reset-yuna-88',
        secret_note: 'homepage banner review'
      },
      {
        employee_id: 'ACM-1116',
        username: 'leo',
        email: 'leo@corp.local',
        full_name: 'Leo Shin',
        title: 'Logistics Coordinator',
        department: 'Operations',
        location: 'Incheon Warehouse',
        phone_ext: '4140',
        role: 'user',
        reset_token: 'reset-leo-39',
        secret_note: 'seat map sync done'
      },
      {
        employee_id: 'ACM-1121',
        username: 'minji',
        email: 'minji@corp.local',
        full_name: 'Minji Seo',
        title: 'Operations Analyst',
        department: 'Operations',
        location: 'Seoul HQ',
        phone_ext: '2039',
        role: 'ops',
        reset_token: 'reset-minji-51',
        secret_note: 'vendor call moved to 4pm'
      },
      {
        employee_id: 'ACM-1128',
        username: 'eric',
        email: 'eric@corp.local',
        full_name: 'Eric Yoon',
        title: 'Backend Engineer',
        department: 'Engineering',
        location: 'Remote',
        phone_ext: '3304',
        role: 'engineering',
        reset_token: 'reset-eric-72',
        secret_note: 'staging deploy completed'
      },
      {
        employee_id: 'ACM-1132',
        username: 'bella',
        email: 'bella@corp.local',
        full_name: 'Bella Song',
        title: 'Product Designer',
        department: 'Design',
        location: 'Seoul HQ',
        phone_ext: '2718',
        role: 'design',
        reset_token: 'reset-bella-41',
        secret_note: 'icon export package sent'
      },
      {
        employee_id: 'ACM-1145',
        username: 'ryan',
        email: 'ryan@corp.local',
        full_name: 'Ryan Oh',
        title: 'Security Analyst',
        department: 'Security',
        location: 'Seoul HQ',
        phone_ext: '3901',
        role: 'security',
        reset_token: 'reset-ryan-09',
        secret_note: 'weekly audit report drafted'
      },
      {
        employee_id: 'ACM-1150',
        username: 'grace',
        email: 'grace@corp.local',
        full_name: 'Grace Lim',
        title: 'Recruiting Coordinator',
        department: 'HR',
        location: 'Seoul HQ',
        phone_ext: '1499',
        role: 'hr',
        reset_token: 'reset-grace-29',
        secret_note: 'interview schedule adjusted'
      },
      {
        employee_id: 'ACM-1164',
        username: 'owen',
        email: 'owen@corp.local',
        full_name: 'Owen Baek',
        title: 'Data Engineer',
        department: 'Engineering',
        location: 'Remote',
        phone_ext: '3362',
        role: 'engineering',
        reset_token: 'reset-owen-58',
        secret_note: 'warehouse metrics pipeline rerun'
      },
      {
        employee_id: 'ACM-1177',
        username: 'iris',
        email: 'iris@corp.local',
        full_name: 'Iris Moon',
        title: 'Field Support Coordinator',
        department: 'Support',
        location: 'Daegu Office',
        phone_ext: '5216',
        role: 'support',
        reset_token: 'reset-iris-14',
        secret_note: 'replacement headset requested'
      }
    ]
  });

  console.log('[+] seed complete');
}

main()
  .catch((err) => {
    console.error(err);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
