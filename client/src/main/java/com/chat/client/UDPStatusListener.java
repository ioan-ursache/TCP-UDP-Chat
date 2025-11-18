package com.chat.client;

import javafx.application.Platform;
import org.json.JSONArray;
import org.json.JSONObject;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.util.function.Consumer;

/**
 * UDP Listener pentru status broadcasts
 * Primește mesaje de tip join/leave/typing/presence
 */
public class UDPStatusListener {
    private DatagramSocket socket;
    private int port;
    private boolean running = false;
    private Thread listenerThread;
    private Consumer<String> statusHandler;

    /**
     * Constructor
     * @param port - port UDP pentru listening
     * @param statusHandler - callback pentru status updates
     */
    public UDPStatusListener(int port, Consumer<String> statusHandler) {
        this.port = port;
        this.statusHandler = statusHandler;
    }

    /**
     * Start listening for UDP broadcasts
     */
    public boolean start() {
        try {
            socket = new DatagramSocket(port);
            socket.setBroadcast(true);
            socket.setReuseAddress(true);
            running = true;

            System.out.println("[UDP] Listening on port " + port);

            listenerThread = new Thread(this::listen);
            listenerThread.setDaemon(true);
            listenerThread.start();

            return true;

        } catch (Exception e) {
            System.err.println("[UDP] Failed to start: " + e.getMessage());
            return false;
        }
    }

    /**
     * Listen for UDP packets
     */
    private void listen() {
        byte[] buffer = new byte[1024];

        while (running) {
            try {
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);

                String data = new String(packet.getData(), 0, packet.getLength(), "UTF-8");
                handleStatusMessage(data);

            } catch (Exception e) {
                if (running) {
                    System.err.println("[UDP] Receive error: " + e.getMessage());
                }
            }
        }
    }

    /**
     * Handle incoming status message
     */
    private void handleStatusMessage(String jsonStr) {
        try {
            JSONObject msg = new JSONObject(jsonStr);

            if (!"status".equals(msg.getString("type"))) {
                return;
            }

            String status = msg.getString("status");
            String formatted = null;

            switch (status) {
                case "join":
                    String joinUser = msg.getString("user");
                    formatted = "[UDP] " + joinUser + " joined the network";
                    break;

                case "leave":
                    String leaveUser = msg.getString("user");
                    formatted = "[UDP] " + leaveUser + " left the network";
                    break;

                case "typing":
                    String typingUser = msg.getString("user");
                    formatted = "[UDP] " + typingUser + " is typing...";
                    break;

                case "presence":
                    JSONArray users = msg.getJSONArray("users");
                    StringBuilder sb = new StringBuilder("[UDP] Active users: ");
                    for (int i = 0; i < users.length(); i++) {
                        if (i > 0) sb.append(", ");
                        sb.append(users.getString(i));
                    }
                    formatted = sb.toString();
                    break;
            }

            if (formatted != null) {
                final String message = formatted;
                Platform.runLater(() -> {
                    if (statusHandler != null) {
                        statusHandler.accept(message);
                    }
                });
            }

        } catch (Exception e) {
            // Ignore malformed UDP packets
            System.err.println("[UDP] Parse error: " + e.getMessage());
        }
    }

    /**
     * Stop listening
     */
    public void stop() {
        running = false;
        if (socket != null && !socket.isClosed()) {
            socket.close();
        }
        System.out.println("[UDP] Stopped");
    }

    public boolean isRunning() {
        return running;
    }
}
