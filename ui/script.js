// Variables globales
let currentSpeech = null;
let selectedVoice = null;
let recognition = null;
let isListening = false;
let recognitionTimeout = null;
let isFirstInteraction = true; // NOUVEAU: pour suivre la première interaction

// Configuration de l'API
const API_CONFIG = {
    URL: 'http://127.0.0.1:5000/ask',
    TIMEOUT: 30000
};

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
    
    // Bouton micro
    document.getElementById('voiceBtn').addEventListener('click', toggleSpeechRecognition);
    
    // Suggestions rapides - MODIFIÉ pour utiliser handleUserMessage
    document.querySelectorAll('.suggestion').forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            const suggestionText = this.getAttribute('data-text');
            handleUserMessage(suggestionText);
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

// NOUVELLE FONCTION: Gérer les messages utilisateur (unifie l'envoi)
async function handleUserMessage(message) {
    if (message.trim() === '') return;

    // Ajouter le message de l'utilisateur
    addUserMessage(message);
    
    // Afficher un indicateur de chargement
    const loadingMessage = addLoadingMessage();
    
    try {
        let botResponse;
        
        // Si c'est la première interaction, utiliser les réponses par défaut
        if (isFirstInteraction) {
            botResponse = getDefaultResponse(message);
            isFirstInteraction = false; // Passer au backend pour les prochaines interactions
        } else {
            // Utiliser l'API backend pour les interactions suivantes
            botResponse = await callChatbotAPI(message);
        }
        
        // Supprimer le message de chargement
        removeLoadingMessage(loadingMessage);
        
        // Ajouter la réponse du bot
        addBotMessage(botResponse);
        
    } catch (error) {
        // En cas d'erreur, supprimer le loading et afficher un message d'erreur
        removeLoadingMessage(loadingMessage);
        
        const errorMessage = "Désolé, je rencontre des difficultés techniques. Pouvez-vous réessayer ?";
        addBotMessage(errorMessage);
        
        console.error('Erreur dans handleUserMessage:', error);
    }

    // Vider le champ de saisie
    document.getElementById('userInput').value = '';
    updateVoiceStatus('idle');
}

// FONCTION: Réponses par défaut pour la première interaction
function getDefaultResponse(userMessage) {
    const defaultResponses = {
        // Réponses pour les suggestions
        "Je souhaite arrêter de fumer": "Excellent décision ! L'arrêt du tabac est l'une des meilleures choses que vous puissiez faire pour votre santé. Je peux vous accompagner avec des stratégies personnalisées. Parlez-moi de votre consommation actuelle.",
        "J'aimerais réduire ma consommation d'alcool": "Je vous comprends. La réduction de la consommation d'alcool peut avoir des bénéfices importants sur la santé. Pouvez-vous me décrire vos habitudes actuelles ?",
        "J'ai besoin d'aide pour une addiction": "Je suis là pour vous aider. Pouvez-vous me parler de ce qui vous préoccupe particulièrement ? Plus vous me donnerez de détails, mieux je pourrai vous orienter.",
        
        // Réponses génériques
        "bonjour": "Bonjour ! Je suis NAFASS, votre assistant spécialisé en addictologie. Comment puis-je vous aider aujourd'hui ?",
        "salut": "Salut ! Je suis là pour vous accompagner. De quoi aimeriez-vous parler ?",
        "merci": "Je vous en prie ! N'hésitez pas si vous avez d'autres questions ou préoccupations.",
        "aide": "Bien sûr ! Je peux vous aider avec les addictions au tabac, à l'alcool, aux drogues, ou d'autres dépendances. De quoi avez-vous besoin ?"
    };

    // Chercher une réponse spécifique, sinon réponse générique
    const lowerMessage = userMessage.toLowerCase();
    
    for (const [key, response] of Object.entries(defaultResponses)) {
        if (lowerMessage.includes(key.toLowerCase())) {
            return response;
        }
    }

    // Réponse par défaut si aucun match
    return "Je comprends votre message. Pour vous offrir le meilleur accompagnement, je vais maintenant utiliser mes connaissances spécialisées. Pouvez-vous reformuler votre question ?";
}

// FONCTION: Appeler l'API backend
async function callChatbotAPI(question) {
    console.log('📡 Envoi à l\'API backend:', question);
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

        const response = await fetch(API_CONFIG.URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Réponse du backend:', data);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        return data.answer;
        
    } catch (error) {
        console.error('❌ Erreur API:', error);
        
        if (error.name === 'AbortError') {
            throw new Error('La requête a pris trop de temps. Veuillez réessayer.');
        }
        
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Impossible de se connecter au serveur. Vérifiez que le backend est démarré.');
        }
        
        throw error;
    }
}

// FONCTION: Ajouter un message de chargement
function addLoadingMessage() {
    const chatMessages = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading';
    loadingDiv.id = 'loading-message';
    loadingDiv.innerHTML = `
        <div class="message-avatar">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" alt="NAFASS">
        </div>
        <div class="message-content">
            <p>NAFASS réfléchit...</p>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return loadingDiv;
}

// FONCTION: Supprimer le message de chargement
function removeLoadingMessage(loadingElement) {
    if (loadingElement && loadingElement.parentNode) {
        loadingElement.parentNode.removeChild(loadingElement);
    }
}

// MODIFICATION: Fonction sendMessage utilisant handleUserMessage
function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    handleUserMessage(message);
}

// MODIFICATION: Fonction sendSuggestion utilisant handleUserMessage
function sendSuggestion(text) {
    document.getElementById('userInput').value = text;
    handleUserMessage(text);
}

// Le reste du code reste identique (STT, TTS, etc.)
// Initialisation de la reconnaissance vocale CORRIGÉE
function initializeSpeechRecognition() {
    // Vérifier la compatibilité du navigateur
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.warn('La reconnaissance vocale n\'est pas supportée par ce navigateur');
        document.getElementById('voiceBtn').style.display = 'none';
        updateVoiceStatus('error', 'Reconnaissance vocale non supportée');
        return;
    }

    try {
        // Créer l'instance de reconnaissance vocale
        recognition = new SpeechRecognition();
        
        // Configuration OPTIMISÉE
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'fr-FR';
        recognition.maxAlternatives = 3; // Augmenté pour plus de précision
        
        // Événements de reconnaissance
        recognition.onstart = function() {
            console.log('🎤 Reconnaissance vocale démarrée');
            isListening = true;
            updateVoiceStatus('listening');
            
            // Timeout de sécurité pour éviter les blocages
            clearTimeout(recognitionTimeout);
            recognitionTimeout = setTimeout(() => {
                if (isListening) {
                    console.log('⏱️ Timeout de sécurité - arrêt de la reconnaissance');
                    recognition.stop();
                }
            }, 10000); // 10 secondes max
        };

        recognition.onresult = function(event) {
            console.log('🎯 Résultat de reconnaissance reçu');
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                const transcript = result[0].transcript;
                
                if (result.isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }

            // Mettre à jour le champ de saisie
            const userInput = document.getElementById('userInput');
            
            if (finalTranscript) {
                userInput.value = finalTranscript.trim();
                updateVoiceStatus('success', 'Texte transcrit avec succès');
                
                // Arrêter automatiquement après un résultat final
                setTimeout(() => {
                    if (isListening) {
                        recognition.stop();
                    }
                }, 500);
                
            } else if (interimTranscript) {
                userInput.value = interimTranscript;
                updateVoiceStatus('listening', 'En cours de transcription...');
            }
        };

        recognition.onerror = function(event) {
            console.error('❌ Erreur de reconnaissance vocale:', event.error);
            isListening = false;
            clearTimeout(recognitionTimeout);
            
            let errorMessage = 'Erreur de reconnaissance';
            switch (event.error) {
                case 'not-allowed':
                case 'permission-denied':
                    errorMessage = 'Microphone non autorisé. Veuillez autoriser l\'accès au microphone dans les paramètres de votre navigateur.';
                    break;
                case 'audio-capture':
                    errorMessage = 'Aucun microphone détecté. Vérifiez votre périphérique audio.';
                    break;
                case 'network':
                    errorMessage = 'Erreur réseau. Vérifiez votre connexion internet.';
                    break;
                case 'no-speech':
                    errorMessage = 'Aucune parole détectée. Veuillez parler plus fort ou plus clairement.';
                    break;
                case 'aborted':
                    errorMessage = 'Reconnaissance annulée.';
                    break;
                default:
                    errorMessage = 'Erreur technique: ' + event.error;
            }
            
            updateVoiceStatus('error', errorMessage);
            
            // Réinitialiser après une erreur
            setTimeout(() => {
                updateVoiceStatus('idle');
            }, 3000);
        };

        recognition.onend = function() {
            console.log('🛑 Reconnaissance vocale terminée');
            isListening = false;
            clearTimeout(recognitionTimeout);
            
            if (!document.getElementById('voiceStatus').classList.contains('error')) {
                updateVoiceStatus('idle');
            }
        };

        console.log('✅ Reconnaissance vocale initialisée avec succès');

    } catch (error) {
        console.error('❌ Erreur lors de l\'initialisation de la reconnaissance:', error);
        updateVoiceStatus('error', 'Erreur d\'initialisation: ' + error.message);
    }
}

// Fonction pour basculer la reconnaissance vocale AMÉLIORÉE
function toggleSpeechRecognition() {
    if (!recognition) {
        updateVoiceStatus('error', 'Reconnaissance vocale non disponible');
        return;
    }

    // Arrêter la synthèse vocale en cours
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }

    if (isListening) {
        console.log('🛑 Arrêt manuel de la reconnaissance');
        recognition.stop();
        updateVoiceStatus('idle');
    } else {
        try {
            console.log('🎤 Démarrage de la reconnaissance vocale');
            
            // Vider le champ de saisie avant de commencer
            document.getElementById('userInput').value = '';
            
            // Délai court pour éviter les conflits
            setTimeout(() => {
                recognition.start();
                updateVoiceStatus('starting');
            }, 100);
            
        } catch (error) {
            console.error('❌ Erreur au démarrage:', error);
            
            if (error.message.includes('already started')) {
                // La reconnaissance est déjà en cours, on l'arrête et on redémarre
                recognition.stop();
                setTimeout(() => {
                    recognition.start();
                    updateVoiceStatus('starting');
                }, 500);
            } else {
                updateVoiceStatus('error', 'Impossible de démarrer: ' + error.message);
            }
        }
    }
}

// Fonction pour mettre à jour le statut de la dictée
function updateVoiceStatus(state, message = '') {
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceStatus = document.getElementById('voiceStatus');
    const userInput = document.getElementById('userInput');

    // Réinitialiser les classes
    voiceBtn.classList.remove('listening', 'error', 'success', 'starting');
    voiceStatus.className = 'voice-status';

    switch (state) {
        case 'starting':
            voiceBtn.classList.add('starting');
            voiceStatus.innerHTML = '🎤 Initialisation...';
            voiceStatus.classList.add('info');
            userInput.placeholder = 'Initialisation du micro...';
            break;

        case 'listening':
            voiceBtn.classList.add('listening');
            voiceStatus.innerHTML = '🎤 ' + (message || 'Écoute en cours... Parlez maintenant');
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
            userInput.placeholder = 'Tapez votre message...';
            break;

        case 'idle':
        default:
            voiceBtn.classList.remove('listening', 'error', 'success');
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
    
    heroSection.style.opacity = '0';
    heroSection.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        heroSection.style.display = 'none';
        chatbotInterface.style.display = 'flex';
        
        setTimeout(() => {
            chatbotInterface.style.opacity = '1';
            chatbotInterface.style.transform = 'translateY(0)';
        }, 50);
    }, 500);
}

// Système de voix
function findBestFrenchVoice() {
    const voices = window.speechSynthesis.getVoices();
    
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
            return voice;
        }
    }

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

// Charger les voix
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