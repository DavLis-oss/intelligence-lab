const fs = require('fs');
const path = require('path');

const postsDirectory = path.join(__dirname, '_posts');
const outputFile = path.join(__dirname, 'posts.json');

const files = fs.readdirSync(postsDirectory);

const posts = files
  .filter(file => file.endsWith('.md'))
  .map(file => {
    const content = fs.readFileSync(path.join(postsDirectory, file), 'utf8');
    // On extrait le titre de la première ligne (# Titre) ou du nom de fichier
    const titleMatch = content.match(/^#\s+(.*)/m);
    const title = titleMatch ? titleMatch[1] : file.replace('.md', '');
    
    // On prend les 150 premiers caractères pour l'extrait
    const excerpt = content.replace(/#+\s/g, '').slice(0, 150).trim() + '...';

    return {
      id: file.replace('.md', ''),
      date: file.substring(0, 10), // Extrait la date du nom de fichier (ex: 2026-03-21)
      title: title,
      excerpt: excerpt
    };
  })
  .sort((a, b) => b.id.localeCompare(a.id)); // Les plus récents en premier

fs.writeFileSync(outputFile, JSON.stringify(posts, null, 2));
console.log('posts.json généré avec succès.');
