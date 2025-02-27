const { Telegraf } = require('telegraf');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Handle deep links: https://t.me/your_bot?start=MOVIE_ID
bot.start(async (ctx) => {
    const movieId = ctx.startPayload;
    
    // Get file details from Supabase
    const { data, error } = await supabase
        .from('movies')
        .select('*')
        .eq('id', movieId)
        .single();

    if (!data || error) {
        return ctx.reply('File not found 😞');
    }

    // Send file through Telegram
    if (data.telegram_file_id) {
        await ctx.replyWithDocument(data.telegram_file_id, {
            caption: `📁 ${data.title}\n✅ Ready to download!`
        });
    }
    // Fallback to URL
    else if (data.cloud_download_url) {
        await ctx.reply(`Here's your download link:\n${data.cloud_download_url}`);
    }
});

// ADMIN: Upload files to Supabase
bot.command('upload', async (ctx) => {
    // Get your Telegram ID using @userinfobot
    if (ctx.from.id.toString() !== process.env.ADMIN_ID) return;

    const file = ctx.message.document;
    if (!file) return ctx.reply('Send a file with this command');

    try {
        // Get Telegram file ID
        const fileId = file.file_id;
        
        // Store in Supabase
        const { data, error } = await supabase
            .from('movies')
            .insert({
                id: file.file_name.split('.')[0], // Use filename as ID
                title: file.file_name,
                telegram_file_id: fileId
            });

        ctx.reply(`File uploaded! Users can access via:\nhttps://yourusername.github.io/file-redirect/?id=${file.file_name.split('.')[0]}`);
    } catch (error) {
        ctx.reply('Upload failed: ' + error.message);
    }
});

// Webhook setup
bot.launch({
    webhook: {
        domain: process.env.RENDER_URL,
        port: process.env.PORT || 3000
    }
});
