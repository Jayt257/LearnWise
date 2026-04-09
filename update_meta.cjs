const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname, 'public', 'data', 'languages');
const templateMetaPath = path.join(baseDir, 'hi', 'ja', 'meta.json');

try {
  const templateMeta = JSON.parse(fs.readFileSync(templateMetaPath, 'utf8'));
  const monthsData = templateMeta.months;

  const pairs = ['hi/en', 'en/hi', 'en/ja', 'ja/hi', 'ja/en'];

  pairs.forEach(pair => {
    const p = pair.split('/');
    const metaPath = path.join(baseDir, p[0], p[1], 'meta.json');
    if (fs.existsSync(metaPath)) {
      const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
      meta.months = monthsData; // copy the 2 months structure
      meta.status = "active";
      fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
      console.log(`Updated meta.json for ${pair}`);
    } else {
      console.log(`Not found: ${metaPath}`);
    }
  });
} catch(e) {
  console.error(e);
}
