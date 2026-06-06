importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');
importScripts('/firebase-config-sw.js');

const firebaseConfig = self.__TRACE_NET_FIREBASE_CONFIG__ || {};

if (firebaseConfig.apiKey && firebaseConfig.messagingSenderId) {
    firebase.initializeApp(firebaseConfig);
    const messaging = firebase.messaging();

    messaging.onBackgroundMessage(function(payload) {
        const notification = payload.notification || {};
        const title = notification.title || 'TraceNet Alert';
        const options = {
            body: notification.body || '',
            icon: notification.icon || '/static/favicon.ico',
            data: payload.data || {}
        };
        self.registration.showNotification(title, options);
    });
} else {
    console.warn('Firebase messaging service worker initialized without config.');
}
