var express = require('express');
var app = express();

app.use(express.static('.'));

// Expose le dossier meshes pour les modèles 3D générés
app.use('/meshes', express.static(__dirname + '/meshes'));

// Route spéciale pour Kibalone Studio
app.get('/studio', function(req, res) {
    res.sendFile(__dirname + '/kibalone-studio.html');
});

app.listen(3000, function() {
    console.log('🚀 Kibalone Studio server listening on port 3000');
    console.log('📺 Interface classique: http://localhost:3000');
    console.log('🎨 Kibalone Studio: http://localhost:3000/studio');
    console.log('🎯 Meshes: http://localhost:3000/meshes/');
});
