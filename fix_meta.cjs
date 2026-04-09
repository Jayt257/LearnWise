const fs = require('fs');
const path = require('path');

const basePath = path.join(__dirname, 'public', 'data', 'languages');
const paths = ['hi/en', 'en/hi', 'en/ja', 'ja/hi', 'ja/en'];

paths.forEach(p => {
  const metaPath = path.join(basePath, p, 'meta.json');
  if (fs.existsSync(metaPath)) {
    const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
    meta.months.forEach(m => {
      // Move activities array into a week
      if (m.activities && m.activities.length > 0) {
        m.weeks = [
          {
            week: 1,
            title: "Week 1",
            activities: m.activities
          }
        ];
        delete m.activities; // Remove the un-nested activities
      }
    });
    fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
    console.log(`Fixed meta.json for ${p}`);
  }
});
