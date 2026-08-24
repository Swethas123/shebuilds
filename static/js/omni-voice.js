/**
 * OmniConnect - Universal Voice & Emotion Recognition Engine
 * Handles Speech-to-Text, Emotion Tone Analysis, Text-to-Speech, 
 * Mock Technician Calling, and OmniDimension Integration.
 */

window.OmniVoice = (function () {
  let recognition = null;
  let isListening = false;
  let currentEmotion = 'neutral';
  let callTimerInterval = null;
  let callSeconds = 0;
  let audioCtx = null;
  let ringOscillator = null;

  // Emotion Keyword Rules
  const emotionDictionary = {
    urgent: ['emergency', 'urgent', 'danger', 'fire', 'burst', 'flooding', 'spark', 'shock', 'stuck in lift', 'immediately', 'critical', 'severe'],
    frustrated: ['terrible', 'worst', 'angry', 'frustrated', 'unacceptable', 'delay', 'again', 'third time', 'annoying', 'nobody came', 'complaint'],
    happy: ['great', 'awesome', 'thank', 'resolved', 'wonderful', 'happy', 'excited', 'party', 'enjoy', 'good job', 'love'],
    neutral: ['issue', 'problem', 'repair', 'light', 'tap', 'water', 'cleaning', 'lift', 'fan', 'switch', 'door', 'gym', 'garden']
  };

  function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('SpeechRecognition API not supported on this browser.');
      return null;
    }

    const reco = new SpeechRecognition();
    reco.continuous = false;
    reco.interimResults = true;
    reco.lang = 'en-US';

    reco.onstart = function () {
      isListening = true;
      updateListeningUI(true);
      showOmniToast('🎤 Listening... Speak now', 'info');
    };

    reco.onresult = function (event) {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const text = finalTranscript || interimTranscript;
      const transcriptBox = document.getElementById('voiceTranscript');
      if (transcriptBox) {
        transcriptBox.innerHTML = `<span>🗣️ "${text}"</span>`;
      }

      // Analyze Emotion
      if (text.length > 3) {
        const detected = analyzeEmotion(text);
        setEmotion(detected);
        processVoiceCommands(text);
      }
    };

    reco.onerror = function (e) {
      console.error('Speech recognition error:', e.error);
      isListening = false;
      updateListeningUI(false);
      if (e.error === 'not-allowed') {
        showOmniToast('⚠️ Microphone access blocked. Please allow permission.', 'error');
      }
    };

    reco.onend = function () {
      isListening = false;
      updateListeningUI(false);
    };

    return reco;
  }

  function toggleListening() {
    if (!recognition) {
      recognition = initSpeechRecognition();
    }
    if (!recognition) {
      showOmniToast('Speech recognition unavailable in this browser.', 'warning');
      return;
    }

    if (isListening) {
      recognition.stop();
    } else {
      try {
        recognition.start();
      } catch (err) {
        console.error('Error starting recognition:', err);
      }
    }
  }

  function updateListeningUI(active) {
    const ring = document.getElementById('emotionRing');
    const wave = document.getElementById('voiceWave');
    const micBtn = document.getElementById('micToggleBtn');

    if (ring) {
      if (active) ring.classList.add('listening');
      else ring.classList.remove('listening');
    }
    if (wave) {
      if (active) wave.classList.add('active');
      else wave.classList.remove('active');
    }
    if (micBtn) {
      micBtn.innerHTML = active ? '⏹️ Stop' : '🎤 Speak Now';
    }
  }

  function analyzeEmotion(text) {
    const lower = text.toLowerCase();
    for (let word of emotionDictionary.urgent) {
      if (lower.includes(word)) return 'urgent';
    }
    for (let word of emotionDictionary.frustrated) {
      if (lower.includes(word)) return 'frustrated';
    }
    for (let word of emotionDictionary.happy) {
      if (lower.includes(word)) return 'happy';
    }
    return 'neutral';
  }

  function setEmotion(emotion) {
    currentEmotion = emotion;
    const ring = document.getElementById('emotionRing');
    const icon = document.getElementById('emotionIcon');
    const badge = document.getElementById('emotionBadge');
    const prioritySelect = document.getElementById('priorityInput');

    const emotionMeta = {
      urgent: { icon: '🚨', label: 'Urgent Tone (Critical)', class: 'emotion-urgent', priority: 'P1' },
      frustrated: { icon: '😠', label: 'Frustrated Tone (High)', class: 'emotion-frustrated', priority: 'P2' },
      neutral: { icon: '😐', label: 'Neutral Tone (Standard)', class: 'emotion-neutral', priority: 'P3' },
      happy: { icon: '😊', label: 'Calm / Positive Tone', class: 'emotion-happy', priority: 'P4' }
    };

    const meta = emotionMeta[emotion] || emotionMeta.neutral;

    if (ring) {
      ring.className = `emotion-ring ${meta.class} ${isListening ? 'listening' : ''}`;
    }
    if (icon) {
      icon.innerText = meta.icon;
    }
    if (badge) {
      badge.innerText = meta.label;
    }
    if (prioritySelect) {
      prioritySelect.value = meta.priority;
    }
  }

  function processVoiceCommands(transcript) {
    const lower = transcript.toLowerCase();

    // 1. Complaint Auto-fill Parser
    const descField = document.getElementById('descriptionInput');
    const issueSelect = document.getElementById('problemTypeInput');
    const flatInput = document.getElementById('hnoInput');

    if (descField && (document.activeElement === descField || !descField.value)) {
      descField.value = transcript;
    }

    if (issueSelect) {
      if (lower.includes('water') || lower.includes('pipe') || lower.includes('leak') || lower.includes('tap') || lower.includes('plumb')) {
        issueSelect.value = 'Plumbing';
      } else if (lower.includes('power') || lower.includes('light') || lower.includes('electric') || lower.includes('wire') || lower.includes('spark')) {
        issueSelect.value = 'Electrical';
      } else if (lower.includes('lift') || lower.includes('elevator')) {
        issueSelect.value = 'Lift/Elevator';
      } else if (lower.includes('clean') || lower.includes('garbage') || lower.includes('trash') || lower.includes('sweep')) {
        issueSelect.value = 'Sanitation & Cleaning';
      } else if (lower.includes('security') || lower.includes('gate') || lower.includes('guard') || lower.includes('cctv')) {
        issueSelect.value = 'Security & Access';
      }
    }

    // Flat / House Number extraction
    if (flatInput && !flatInput.value) {
      const match = lower.match(/(?:flat|flat number|apartment|room|house|block|#)\s*([a-zA-Z0-9\-\s]+)/);
      if (match && match[1]) {
        flatInput.value = match[1].trim().toUpperCase();
      }
    }

    // 2. Ticket Status Voice Check
    if (lower.includes('status of ticket') || lower.includes('ticket status') || lower.includes('update on ticket') || lower.includes('track ticket')) {
      const numMatch = lower.match(/\b\d{4,6}\b/);
      if (numMatch) {
        checkTicketStatusVoice(numMatch[0]);
      }
    }
  }

  function speakText(text) {
    if (!window.speechSynthesis) {
      showOmniToast('Speech synthesis unavailable.', 'warning');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.05;
    window.speechSynthesis.speak(utterance);
  }

  function checkTicketStatusVoice(ticketNumber) {
    fetch(`/api/ticket-status/${ticketNumber}`)
      .then(res => res.json())
      .then(data => {
        if (data.found) {
          const msg = `Ticket #${ticketNumber} for ${data.category} is currently ${data.status}. Assigned to technician ${data.handleby || 'Duty Team'}.`;
          speakText(msg);
          showOmniToast(msg, 'info');
        } else {
          const notFoundMsg = `Ticket #${ticketNumber} was not found. Please verify the ticket ID.`;
          speakText(notFoundMsg);
          showOmniToast(notFoundMsg, 'warning');
        }
      })
      .catch(() => {
        speakText(`Checking ticket ${ticketNumber}. Live records loaded on your tracking screen.`);
      });
  }

  // ==========================================
  // Mock Technician Call Simulator
  // ==========================================
  function startTechnicianCall(techName, techSkill, phone) {
    const modal = document.getElementById('techCallModal');
    if (!modal) return;

    modal.classList.add('active');
    document.getElementById('callTechName').innerText = techName || 'Ramesh Kumar';
    document.getElementById('callTechSkill').innerText = techSkill || 'Senior Electrician & Plumber';
    document.getElementById('callTechPhone').innerText = phone || '+91 98401 22345';
    document.getElementById('callStatusText').innerText = 'Ringing...';
    document.getElementById('callDuration').innerText = '00:00';

    playRingtone();

    // Auto-connect after 2.5s
    setTimeout(() => {
      stopRingtone();
      document.getElementById('callStatusText').innerText = 'Connected 🟢 (HD Voice)';
      startCallTimer();
      speakText(`Hello, this is ${techName || 'Rajesh'} from Maintenance support. I have received your society request and am ready to assist you.`);
    }, 2500);
  }

  function endTechnicianCall() {
    stopRingtone();
    clearInterval(callTimerInterval);
    callSeconds = 0;
    if (window.speechSynthesis) window.speechSynthesis.cancel();

    const modal = document.getElementById('techCallModal');
    if (modal) modal.classList.remove('active');
    showOmniToast('📞 Call ended with Technician.', 'info');
  }

  function startCallTimer() {
    clearInterval(callTimerInterval);
    callSeconds = 0;
    callTimerInterval = setInterval(() => {
      callSeconds++;
      const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
      const secs = String(callSeconds % 60).padStart(2, '0');
      const timerEl = document.getElementById('callDuration');
      if (timerEl) timerEl.innerText = `${mins}:${secs}`;
    }, 1000);
  }

  function playRingtone() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      audioCtx = new AudioContext();
      ringOscillator = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();

      ringOscillator.type = 'sine';
      ringOscillator.frequency.setValueAtTime(440, audioCtx.currentTime);
      gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);

      ringOscillator.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      ringOscillator.start();
    } catch (e) {
      console.log('AudioContext error:', e);
    }
  }

  function stopRingtone() {
    try {
      if (ringOscillator) {
        ringOscillator.stop();
        ringOscillator.disconnect();
        ringOscillator = null;
      }
      if (audioCtx) {
        audioCtx.close();
        audioCtx = null;
      }
    } catch (e) {}
  }

  // Quick Toast Notification
  function showOmniToast(message, type = 'info') {
    let container = document.getElementById('omniToastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'omniToastContainer';
      container.className = 'omni-toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'omni-toast';
    const icon = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : type === 'success' ? '✅' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(15px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  return {
    toggleListening,
    speakText,
    setEmotion,
    startTechnicianCall,
    endTechnicianCall,
    showOmniToast,
    checkTicketStatusVoice
  };
})();

// Global helper bindings
window.showOmniToast = window.OmniVoice.showOmniToast;
window.speakOmni = window.OmniVoice.speakText;
window.startTechCall = window.OmniVoice.startTechnicianCall;
window.endTechCall = window.OmniVoice.endTechnicianCall;
