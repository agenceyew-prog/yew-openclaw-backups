const fs = require('fs');

const data = JSON.parse(fs.readFileSync('prospects.json', 'utf8'));
const rows = data.values;
const headers = rows[0];

const statutIndex = headers.indexOf('Statut Contact');
const emailIndex = headers.indexOf('Email');
const nameIndex = headers.indexOf('Nom');
const descIndex = headers.indexOf('Description');
const pitchIndex = headers.indexOf('Angle d\'attaque (Pitch Yew)');
const typeIndex = headers.indexOf('Type d\'organisation');

const toContact = [];

for(let i=1; i<rows.length; i++) {
  const row = rows[i];
  if (row[statutIndex] === 'Non contacté' || !row[statutIndex]) {
     toContact.push({
       index: i + 1,
       name: row[nameIndex],
       email: row[emailIndex],
       desc: row[descIndex],
       pitch: row[pitchIndex],
       type: row[typeIndex],
       events: row[headers.indexOf('Événements sportifs organisés')]
     });
     if (toContact.length === 5) break;
  }
}

console.log(JSON.stringify(toContact, null, 2));
