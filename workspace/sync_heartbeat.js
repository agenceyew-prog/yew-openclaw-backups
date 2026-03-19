const https = require('https');
const fs = require('fs');

const API_KEY = process.env.MATON_API_KEY;
if (!API_KEY) {
    console.error("No MATON_API_KEY found.");
    process.exit(1);
}

const SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ';
const SHEET_NAME = 'Organisateurs Majeurs';

function apiCall(path, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const req = https.request({
            hostname: 'gateway.maton.ai',
            path: path,
            method: method,
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            }
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        resolve(JSON.parse(body));
                    } catch (e) {
                        resolve(body);
                    }
                } else {
                    reject(new Error(`API Error ${res.statusCode}: ${body}`));
                }
            });
        });
        req.on('error', reject);
        if (data) {
            req.write(JSON.stringify(data));
        }
        req.end();
    });
}

async function main() {
    console.log("Fetching Gmail drafts...");
    const draftsRes = await apiCall('/google-mail/gmail/v1/users/me/drafts');
    const drafts = draftsRes.drafts || [];
    const draftEmails = new Set();
    
    for (const d of drafts) {
        const dInfo = await apiCall(`/google-mail/gmail/v1/users/me/messages/${d.message.id}`);
        const headers = dInfo.payload?.headers || [];
        const toHeader = headers.find(h => h.name.toLowerCase() === 'to');
        if (toHeader) {
            const emailMatch = toHeader.value.match(/<([^>]+)>/) || [null, toHeader.value];
            draftEmails.add(emailMatch[1].trim().toLowerCase());
        }
    }
    console.log(`Found ${draftEmails.size} drafts for:`, Array.from(draftEmails));

    console.log("Fetching recent sent emails...");
    // Let's get the 20 most recent sent emails
    const sentRes = await apiCall('/google-mail/gmail/v1/users/me/messages?q=in:sent&maxResults=20');
    const sentMessages = sentRes.messages || [];
    const sentEmails = new Set();
    
    for (const m of sentMessages) {
        const mInfo = await apiCall(`/google-mail/gmail/v1/users/me/messages/${m.id}`);
        const headers = mInfo.payload?.headers || [];
        const toHeader = headers.find(h => h.name.toLowerCase() === 'to');
        if (toHeader) {
            const emailMatch = toHeader.value.match(/<([^>]+)>/) || [null, toHeader.value];
            sentEmails.add(emailMatch[1].trim().toLowerCase());
        }
    }
    console.log(`Found ${sentEmails.size} recent sent emails to:`, Array.from(sentEmails));

    console.log("Fetching Google Sheet data...");
    const sheetData = await apiCall(`/google-sheets/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(SHEET_NAME + '!A1:Z100')}`);
    const rows = sheetData.values || [];
    const headers = rows[0] || [];
    const emailIdx = headers.indexOf('Email');
    const statusIdx = headers.indexOf('Statut Contact');
    
    if (emailIdx === -1 || statusIdx === -1) {
        throw new Error("Missing Email or Statut Contact columns.");
    }
    
    let updates = [];
    
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        let currentStatus = row[statusIdx] || '';
        let email = (row[emailIdx] || '').trim().toLowerCase();
        
        if (!email) continue;
        
        let newStatus = currentStatus;
        if (sentEmails.has(email) && currentStatus !== 'Contacté') {
            newStatus = 'Contacté';
        } else if (draftEmails.has(email) && currentStatus !== 'Brouillon préparé' && currentStatus !== 'Contacté') {
            newStatus = 'Brouillon préparé';
        }
        
        if (newStatus !== currentStatus) {
            console.log(`Row ${i+1} (${email}): updating status '${currentStatus}' -> '${newStatus}'`);
            updates.push({
                range: `${SHEET_NAME}!${String.fromCharCode(65 + statusIdx)}${i + 1}`,
                values: [[newStatus]]
            });
        }
    }
    
    if (updates.length > 0) {
        console.log(`Applying ${updates.length} updates to Google Sheet...`);
        for (const update of updates) {
            await apiCall(`/google-sheets/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(update.range)}?valueInputOption=RAW`, 'PUT', {
                values: update.values
            });
        }
        console.log("Sync complete. Changes made.");
        
        // Notify via Telegram
        const telegramToken = "8755473082:AAHD1ICvFTMMtV0BCSkiaxX7t4r22FhZRiA";
        const chatId = "-5216653116";
        const message = `Léa: J'ai synchronisé le CRM pendant mon heartbeat. ${updates.length} statut(s) de contact mis à jour (emails envoyés ou brouillons).`;
        await apiCall(`/telegram/bot${telegramToken}/sendMessage`, 'POST', {
            chat_id: chatId,
            text: message
        });
        
    } else {
        console.log("CRM is already in sync. No changes needed.");
    }
}

main().catch(console.error);
