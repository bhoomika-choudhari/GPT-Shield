#welcome.py
import streamlit as st
def welcome_screen():
    st.markdown("""
        <style>
        body {
            background-image: url('https://images.unsplash.com/photo-1634942537031-7963b6a3a25f?auto=format&fit=crop&w=1950&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            color: white;
        }

        .centered {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 60px;
        }

        .robot-row {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        /* Mist/glow particles behind robot */
        .robot-row::before {
            content: "";
            position: absolute;
            width: 140px;
            height: 140px;
            background: radial-gradient(circle, rgba(0,255,255,0.2), transparent);
            filter: blur(20px);
            z-index: -1;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            animation: mistPulse 3s ease-in-out infinite;
        }

        /* Wind lines */
        .wind {
            position: absolute;
            left: -40px;
            width: 60px;
            height: 20px;
            border-top: 2px solid rgba(255, 255, 255, 0.4);
            opacity: 0.3;
            filter: blur(1px);
            animation: windmove 2.5s linear infinite;
        }

        .wind2 {
            top: 70px;
            animation-delay: 1.1s;
        }

        .wind3 {
            top: 100px;
            animation-delay: 2.2s;
        }

        @keyframes windmove {
            0% { transform: translateX(0); opacity: 0.2; }
            25% { opacity: 0.5; }
            50% { transform: translateX(50px); opacity: 1; }
            75% { opacity: 0.5; }
            100% { transform: translateX(100px); opacity: 0; }
        }

        @keyframes mistPulse {
            0%, 100% { transform: translateX(-50%) scale(1); opacity: 0.6; }
            50% { transform: translateX(-50%) scale(1.2); opacity: 1; }
        }

        /* Flying in + glow on stop */
        @keyframes flyInGlow {
            0% {
                transform: translateX(-200px) scale(0.5);
                opacity: 0;
                filter: none;
            }
            60% {
                transform: translateX(20px) scale(1.1);
                opacity: 1;
            }
            100% {
                transform: translateX(0) scale(1);
                opacity: 1;
                filter: drop-shadow(0 0 15px #00fff7);
            }
        }

        .robot-img {
            width: 110px;
            animation: flyInGlow 2s ease-out forwards;
            transition: transform 0.3s ease;
            background: transparent !important;
            box-shadow: none !important;
            will-change: transform, opacity;
        }

        .robot-img:hover {
            transform: scale(1.05);
        }

        .logo-gif {
            width: 60px;
            transition: transform 0.3s ease;
        }

        .logo-gif:hover {
            transform: scale(1.05);
        }

        .typewriter h1 {
            overflow: hidden;
            border-right: .15em solid white;
            white-space: nowrap;
            margin: 0 auto;
            animation:
                typing 3s steps(30, end),
                blink-caret .75s step-end infinite;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: white; }
        }

        .subtitle {
            font-size: 18px;
            text-align: center;
            margin-top: 20px;
        }

        @media screen and (max-width: 768px) {
            .robot-row {
                flex-direction: column;
                gap: 10px;
            }
            .robot-img {
                width: 90px;
            }
            .logo-gif {
                width: 50px;
            }
        }
        </style>

        <!-- 🎵 Audio when robot glows in -->
        <audio id="glowSound" autoplay>
            <source src="https://assets.mixkit.co/sfx/download/mixkit-fairy-arcade-sparkle-866.wav" type="audio/mpeg">
        </audio>

        <div class="centered">
            <div class="robot-row">
                <div class="wind"></div>
                <div class="wind wind2"></div>
                <div class="wind wind3"></div>
                <img class="robot-img" src="https://cdn-icons-png.flaticon.com/512/4712/4712102.png" alt="Robot">
                <img class="logo-gif" src="https://media.tenor.com/WsxJ6m2X-6IAAAAi/chatgpt.gif" alt="GPT Logo">
            </div>
            <div class="typewriter"><h1>Welcome to GPT Shield</h1></div>
            <p class="subtitle">Your AI-Powered Writing & Detection Companion</p>
        </div>
    """, unsafe_allow_html=True)
