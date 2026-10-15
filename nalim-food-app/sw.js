// =====================================================================
// NALIM Food Service — Service Worker para Web Push Notifications
// =====================================================================

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// Evento disparado quando o servidor Web Push (Render / VAPID) envia uma notificação
self.addEventListener('push', (event) => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { corpo: event.data.text() };
    }
  }

  const titulo = data.titulo || '🔔 Pedido Pronto na Cozinha!';
  const corpo = data.corpo || 'Há pedidos prontos para recolher e servir aos clientes.';
  const urlDestino = data.url || '/garcom';

  const options = {
    body: corpo,
    icon: 'https://cdn-icons-png.flaticon.com/512/3075/3075977.png',
    badge: 'https://cdn-icons-png.flaticon.com/512/3075/3075977.png',
    vibrate: [350, 150, 350, 150, 600],
    tag: data.tag || 'pedido-pronto',
    renotify: true,
    requireInteraction: true,
    data: {
      url: urlDestino,
      hora: Date.now()
    },
    actions: [
      { action: 'abrir', title: 'Abrir Comanda' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(titulo, options)
  );
});

// Evento ao tocar ou clicar na notificação que chegou no celular
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const urlDestino = (event.notification.data && event.notification.data.url)
    ? event.notification.data.url
    : '/garcom';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Se houver qualquer aba do app aberta, traz para primeiro plano
      for (const client of clientList) {
        if (client.url.includes('/garcom') && 'focus' in client) {
          return client.focus();
        }
      }
      // Se não houver, abre uma nova janela no endereço do garçom
      if (clients.openWindow) {
        return clients.openWindow(urlDestino);
      }
    })
  );
});
