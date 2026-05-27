importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

const firebaseConfig = {
    apiKey: '{{ firebase_config.apiKey }}',
    authDomain: '{{ firebase_config.authDomain }}',
    projectId: '{{ firebase_config.projectId }}',
    messagingSenderId: '{{ firebase_config.messagingSenderId }}',
    appId: '{{ firebase_config.appId }}',
    measurementId: '{{ firebase_config.measurementId }}'
};

if (firebaseConfig.apiKey && firebaseConfig.messagingSenderId) {
    firebase.initializeApp(firebaseConfig);
    const messaging = firebase.messaging();

    messaging.onBackgroundMessage(function(payload) {
        const title = payload.notification ? .title || 'TraceNet Alert';
        const options = {
            body: payload.notification ? .body || '',
            icon: payload.notification ? .icon || '/static/favicon.ico',
            data: payload.data || {}
        };
        self.registration.showNotification(title, options);
    });
} else {
    console.warn('Firebase messaging service worker initialized without config.');
}