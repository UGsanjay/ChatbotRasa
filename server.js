const express = require('express');
const axios = require('axios');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;
const RASA_SERVER_URL = 'http://localhost:5005';

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const conversations = new Map();

function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.post('/chat', async (req, res) => {
    try {
        const { message, sessionId = generateSessionId() } = req.body;
        
        if (!message || message.trim() === '') {
            return res.status(400).json({ 
                error: 'Message is required',
                sessionId: sessionId 
            });
        }

        console.log(`[${sessionId}] User: ${message}`);

        const rasaResponse = await axios.post(`${RASA_SERVER_URL}/webhooks/rest/webhook`, {
            sender: sessionId,
            message: message.trim()
        }, {
            timeout: 30000 
        });

        const botResponses = rasaResponse.data;
        console.log(`[${sessionId}] Bot responses:`, botResponses);

        let recommendedMenus = [];
        
        if (botResponses && botResponses.length > 0) {
            try {
                const trackerResponse = await axios.get(`${RASA_SERVER_URL}/conversations/${sessionId}/tracker`);
                const slots = trackerResponse.data.slots;
                
                if (slots && slots.recommended_menus) {
                    recommendedMenus = slots.recommended_menus;
                }
            } catch (slotError) {
                console.log('Could not retrieve slots:', slotError.message);
            }
        }

        if (!conversations.has(sessionId)) {
            conversations.set(sessionId, []);
        }
        
        const conversation = conversations.get(sessionId);
        conversation.push({
            user: message,
            bot: botResponses.map(r => r.text).filter(Boolean),
            timestamp: new Date().toISOString(),
            menus: recommendedMenus
        });

        if (conversation.length > 50) {
            conversation.splice(0, conversation.length - 50);
        }

        const response = {
            sessionId: sessionId,
            responses: botResponses.map(r => ({
                text: r.text || '',
                buttons: r.buttons || [],
                image: r.image || null,
                custom: r.custom || null
            })),
            recommendedMenus: recommendedMenus,
            timestamp: new Date().toISOString()
        };

        res.json(response);

    } catch (error) {
        console.error('Error communicating with Rasa:', error.message);
        
        let errorMessage = 'Maaf, terjadi kesalahan pada sistem. Silakan coba lagi.';
        
        if (error.code === 'ECONNREFUSED') {
            errorMessage = 'Server Rasa tidak dapat dijangkau. Pastikan Rasa server berjalan di port 5005.';
        } else if (error.code === 'ETIMEDOUT') {
            errorMessage = 'Timeout: Server membutuhkan waktu terlalu lama untuk merespons.';
        }

        res.status(500).json({
            error: errorMessage,
            sessionId: req.body.sessionId || generateSessionId(),
            responses: [{
                text: errorMessage,
                buttons: [],
                image: null,
                custom: null
            }],
            recommendedMenus: []
        });
    }
});

app.get('/conversation/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    const conversation = conversations.get(sessionId) || [];
    
    res.json({
        sessionId,
        conversation,
        messageCount: conversation.length
    });
});

app.delete('/conversation/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    conversations.delete(sessionId);
    
    res.json({
        message: 'Conversation history cleared',
        sessionId
    });
});

app.get('/status', async (req, res) => {
    try {
        const rasaStatus = await axios.get(`${RASA_SERVER_URL}/status`, { timeout: 5000 });
        
        res.json({
            webServer: 'running',
            rasaServer: 'connected',
            rasaVersion: rasaStatus.data.version || 'unknown',
            activeConversations: conversations.size,
            uptime: process.uptime(),
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.json({
            webServer: 'running',
            rasaServer: 'disconnected',
            rasaError: error.message,
            activeConversations: conversations.size,
            uptime: process.uptime(),
            timestamp: new Date().toISOString()
        });
    }
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message
    });
});

app.use('/api/*', (req, res) => {
    res.status(404).json({
        error: 'API endpoint not found'
    });
});

app.listen(PORT, () => {
    console.log(`🚀 Web server running on`);
});

process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});