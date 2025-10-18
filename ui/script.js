// Variables globales
let currentSpeech = null;
let selectedVoice = null;
let recognition = null;
let isListening = false;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeVoices();
    initializeSpeechRecognition();
});

// Initialisation des écouteurs d'événements
function initializeEventListeners() {
    // Bouton de démarrage du chat
    document.getElementById('startChat').addEventListener('click', startChatTransition);
    
    // Bouton d'envoi de message
    document.getElementById('sendMessageBtn').addEventListener('click', sendMessage);
    
    // Entrée clavier dans le champ de saisie
    document.getElementById('userInput').addEventListener('keypress', handleKeyPress);
    
    // BOUTON MICRO AJOUTÉ ICI
    document.getElementById('voiceBtn').addEventListener('click', toggleSpeechRecognition);
    
    // Suggestions rapides
    document.querySelectorAll('.suggestion').forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            sendSuggestion(this.getAttribute('data-text'));
        });
    });
    
    // Boutons de lecture audio
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('speak-btn')) {
            const text = event.target.getAttribute('data-text');
            speakText(text, event.target);
        }
    });
}

// INITIALISATION DE LA RECONNAISSANCE VOCALE AJOUTÉE ICI
function initializeSpeechRecognition() {
    // Vérifier la compatibilité du navigateur
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('La reconnaissance vocale n\'est pas supportée par ce navigateur');
        document.getElementById('voiceBtn').style.display = 'none';
        updateVoiceStatus('error', 'Reconnaissance vocale non supportée');
        return;
    }

    // Créer l'instance de reconnaissance vocale
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    // Configuration
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'fr-FR';
    recognition.maxAlternatives = 1;

    // Événements de reconnaissance
    recognition.onstart = function() {
        console.log('Reconnaissance vocale démarrée');
        isListening = true;
        updateVoiceStatus('listening');
    };

    recognition.onresult = function(event) {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        // Mettre à jour le champ de saisie avec le texte transcrit
        const userInput = document.getElementById('userInput');
        userInput.value = finalTranscript || interimTranscript;
        
        if (finalTranscript) {
            updateVoiceStatus('success', 'Texte transcrit avec succès');
        }
    };

    recognition.onerror = function(event) {
        console.error('Erreur de reconnaissance vocale:', event.error);
        isListening = false;
        
        let errorMessage = 'Erreur de reconnaissance';
        switch (event.error) {
            case 'not-allowed':
                errorMessage = 'Microphone non autorisé. Veuillez autoriser l\'accès au microphone.';
                break;
            case 'audio-capture':
                errorMessage = 'Aucun microphone détecté.';
                break;
            case 'network':
                errorMessage = 'Erreur réseau lors de la reconnaissance.';
                break;
            default:
                errorMessage = 'Erreur: ' + event.error;
        }
        
        updateVoiceStatus('error', errorMessage);
    };

    recognition.onend = function() {
        console.log('Reconnaissance vocale terminée');
        isListening = false;
        if (!document.getElementById('voiceStatus').classList.contains('error')) {
            updateVoiceStatus('idle');
        }
    };
}

// FONCTION POUR BASUCLER LA RECONNAISSANCE VOCALE
function toggleSpeechRecognition() {
    if (!recognition) {
        updateVoiceStatus('error', 'Reconnaissance vocale non disponible');
        return;
    }

    if (isListening) {
        recognition.stop();
        updateVoiceStatus('idle');
    } else {
        try {
            // Vider le champ de saisie avant de commencer
            document.getElementById('userInput').value = '';
            recognition.start();
            updateVoiceStatus('starting');
        } catch (error) {
            console.error('Erreur au démarrage:', error);
            updateVoiceStatus('error', 'Impossible de démarrer la reconnaissance');
        }
    }
}

// FONCTION POUR METTRE À JOUR LE STATUT DE LA DICTÉE
function updateVoiceStatus(state, message = '') {
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceStatus = document.getElementById('voiceStatus');
    const userInput = document.getElementById('userInput');

    // Réinitialiser les classes
    voiceBtn.classList.remove('listening', 'error', 'success');
    voiceStatus.className = 'voice-status';

    switch (state) {
        case 'starting':
            voiceStatus.innerHTML = '🎤 Initialisation de la reconnaissance...';
            voiceStatus.classList.add('info');
            break;

        case 'listening':
            voiceBtn.classList.add('listening');
            voiceStatus.innerHTML = '🎤 Écoute en cours... Parlez maintenant';
            voiceStatus.classList.add('listening');
            userInput.placeholder = 'Parlez maintenant...';
            break;

        case 'success':
            voiceBtn.classList.add('success');
            voiceStatus.innerHTML = '✅ ' + (message || 'Texte transcrit. Cliquez sur envoyer.');
            voiceStatus.classList.add('success');
            userInput.placeholder = 'Tapez votre message ou utilisez le micro...';
            break;

        case 'error':
            voiceBtn.classList.add('error');
            voiceStatus.innerHTML = `❌ ${message}`;
            voiceStatus.classList.add('error');
            userInput.placeholder = 'Tapez votre message ou utilisez le micro...';
            break;

        case 'idle':
        default:
            voiceStatus.innerHTML = '🎤 Cliquez sur le micro pour dicter un message';
            voiceStatus.classList.add('idle');
            userInput.placeholder = 'Tapez votre message ou utilisez le micro...';
            break;
    }
}

// Transition vers le chatbot
function startChatTransition() {
    const heroSection = document.getElementById('heroSection');
    const chatbotInterface = document.getElementById('chatbotInterface');
    
    // Animation de disparition de la section hero
    heroSection.style.opacity = '0';
    heroSection.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        heroSection.style.display = 'none';
        chatbotInterface.style.display = 'flex';
        
        // Animation d'apparition du chatbot
        setTimeout(() => {
            chatbotInterface.style.opacity = '1';
            chatbotInterface.style.transform = 'translateY(0)';
        }, 50);
    }, 500);
}

// Système de voix
function findBestFrenchVoice() {
    const voices = window.speechSynthesis.getVoices();
    console.log('Voix disponibles:', voices.map(v => `${v.name} (${v.lang})`));
    
    // Priorité des voix par qualité
    const voicePreferences = [
        voice => voice.name.includes('Google français') || voice.name.includes('Google French'),
        voice => voice.name.includes('Microsoft') && voice.name.includes('French'),
        voice => voice.lang.startsWith('fr') && voice.name.toLowerCase().includes('female'),
        voice => voice.lang.startsWith('fr') || voice.lang.includes('FR'),
        voice => voice.lang.includes('fr')
    ];

    for (const preference of voicePreferences) {
        const voice = voices.find(preference);
        if (voice) {
            console.log('Voix sélectionnée:', voice.name, voice.lang);
            return voice;
        }
    }

    console.warn('Aucune voix française trouvée, utilisation de la voix par défaut');
    return voices[0] || null;
}

function initializeVoices() {
    selectedVoice = findBestFrenchVoice();
    const voiceInfo = document.getElementById('voiceInfo');
    
    if (selectedVoice) {
        const voiceName = selectedVoice.name.split(' ')[0];
        voiceInfo.innerHTML = `🔊 ${voiceName}`;
        voiceInfo.title = `Voix: ${selectedVoice.name}`;
    } else {
        voiceInfo.innerHTML = '🔇 Voix non disponible';
        voiceInfo.style.color = '#FECACA';
    }
}

// Charger les voix quand elles sont disponibles
if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = initializeVoices;
}

// Fonction de synthèse vocale
function speakText(text, speakBtn) {
    if (currentSpeech) {
        window.speechSynthesis.cancel();
    }

    const speech = new SpeechSynthesisUtterance();
    speech.text = text;
    speech.lang = 'fr-FR';
    speech.rate = 0.85;
    speech.pitch = 1.0;
    speech.volume = 1.0;

    if (selectedVoice) {
        speech.voice = selectedVoice;
    }

    currentSpeech = speech;

    speakBtn.innerHTML = '⏸️ Pause';
    speakBtn.onclick = function() { pauseSpeech(speakBtn); };
    speakBtn.classList.add('playing');

    speech.onstart = function() {
        speakBtn.classList.add('active');
    };

    speech.onend = function() {
        speakBtn.innerHTML = '🔊 Lire le message';
        speakBtn.onclick = function() { speakText(text, speakBtn); };
        speakBtn.classList.remove('playing', 'active');
        currentSpeech = null;
    };

    speech.onerror = function(event) {
        console.error('Erreur de synthèse vocale:', event);
        speakBtn.innerHTML = '🔊 Lire le message';
        speakBtn.onclick = function() { speakText(text, speakBtn); };
        speakBtn.classList.remove('playing', 'active');
        currentSpeech = null;
        
        const voiceInfo = document.getElementById('voiceInfo');
        voiceInfo.innerHTML = '❌ Erreur voix';
        voiceInfo.style.color = '#FECACA';
    };

    window.speechSynthesis.speak(speech);
}

function pauseSpeech(speakBtn) {
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
        window.speechSynthesis.pause();
        speakBtn.innerHTML = '▶️ Reprendre';
        speakBtn.onclick = function() { resumeSpeech(speakBtn); };
    }
}

function resumeSpeech(speakBtn) {
    if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        speakBtn.innerHTML = '⏸️ Pause';
        speakBtn.onclick = function() { pauseSpeech(speakBtn); };
    }
}

// Fonctions du chatbot
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendSuggestion(text) {
    document.getElementById('userInput').value = text;
    sendMessage();
}

function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (message === '') return;

    addUserMessage(message);
    
    setTimeout(() => {
        const responses = [
            "Je comprends votre situation. Pouvez-vous me en dire plus sur ce qui vous motive à changer ?",
            "Merci de partager cela avec moi. Comment vous sentez-vous par rapport à cette situation ?",
            "C'est un bon début de reconnaître ces difficultés. Quel est votre objectif principal ?",
            "Je suis là pour vous accompagner. Depuis combien de temps cette situation dure-t-elle ?"
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addBotMessage(randomResponse);
    }, 1000);

    userInput.value = '';
    updateVoiceStatus('idle');
}

function addUserMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
        </div>
        <div class="message-avatar">
            <img src="https://cdn-icons-png.flaticon.com/512/847/847969.png" alt="Vous">
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addBotMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" alt="NAFASS">
        </div>
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
            <div class="message-actions">
                <button class="speak-btn" data-text="${escapeHtml(text)}">
                    🔊 Lire le message
                </button>
            </div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    const newSpeakBtn = messageDiv.querySelector('.speak-btn');
    newSpeakBtn.addEventListener('click', function() {
        speakText(this.getAttribute('data-text'), this);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

setTimeout(initializeVoices, 1000);