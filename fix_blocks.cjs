const fs = require('fs');
const path = require('path');

const basePath = path.join(__dirname, 'public', 'data', 'languages');
const paths = ['hi/en', 'en/hi', 'en/ja', 'ja/hi', 'ja/en'];

paths.forEach(p => {
  const m1 = path.join(basePath, p, 'month-1');
  if (!fs.existsSync(m1)) return;

  const files = fs.readdirSync(m1);
  files.forEach(f => {
    if (!f.endsWith('.json')) return;
    const fPath = path.join(m1, f);
    const data = JSON.parse(fs.readFileSync(fPath, 'utf8'));

    let modified = false;

    if (data.blocks && Array.isArray(data.blocks)) {
      data.blocks.forEach(b => {
        // Fix multiple_choice -> quiz
        if (b.type === 'multiple_choice') {
          b.type = 'quiz';
          if (b.correctIndex !== undefined) {
            b.correct = b.correctIndex;
            delete b.correctIndex;
          }
          modified = true;
        }

        // Fix speaking_scenario -> speaking
        if (b.type === 'speaking_scenario') {
          b.type = 'speaking';
          b.prompt = b.scenario || b.title || "Please read the text.";
          b.hints = b.hint ? [b.hint, b.expectedAnswer] : [b.expectedAnswer];
          modified = true;
        }

        // Fix pronunciation -> speaking
        if (b.type === 'pronunciation') {
          b.type = 'speaking';
          b.prompt = `Pronounce this word clearly: ${b.word}`;
          b.hints = [`Meaning: ${b.meaning}`, `Target: ${b.word}`];
          modified = true;
        }
      });
    }

    if (modified) {
      fs.writeFileSync(fPath, JSON.stringify(data, null, 2));
      console.log(`Patched block types inside ${p} / ${f}`);
    }
  });
});
