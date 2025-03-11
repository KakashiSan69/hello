const express = require('express');
const ytdl = require('@distube/ytdl-core');

const app = express();
const PORT = process.env.PORT || 5000;

app.get('/download', async (req, res) => {
    const videoURL = req.query.url;
    
    if (!ytdl.validateURL(videoURL)) {
        return res.status(400).json({ error: 'Invalid YouTube URL' });
    }

    try {
        const info = await ytdl.getInfo(videoURL);
        const title = info.videoDetails.title.replace(/[^\w\s]/gi, '');

        res.header('Content-Disposition', `attachment; filename="${title}.mp4"`);
        ytdl(videoURL, {
            filter: 'audioandvideo',
            format: 'mp4',
        }).pipe(res);

    } catch (err) {
        res.status(500).json({ error: 'Failed to process the video', details: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
