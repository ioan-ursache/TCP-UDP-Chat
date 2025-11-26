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
    private DatagramSocket socket; // UDP socket
    private int port; // port UDP
    private boolean running = false; // marks status of listener
    private Thread listenerThread; // thread for listening UDP packets
    private Consumer<String> statusHandler; // callback for status updates

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
     * Asculta pentru status broadcasts UDP
     */
    public boolean start() {
        try {
            socket = new DatagramSocket(port); // create UDP socket
            socket.setBroadcast(true); // allow broadcasting
            socket.setReuseAddress(true); // useful for before binding to the same port
            running = true;

            System.out.println("[UDP] Listening on port " + port);

            listenerThread = new Thread(this::listen); // add thread
            listenerThread.setDaemon(true); // sets Thread as Daemon, it will not work in the background of the client
            listenerThread.start(); // start thread

            return true;

        } catch (Exception e) {
            System.err.println("[UDP] Failed to start: " + e.getMessage());
            return false;
        }
    }

    /**
     * Asculta pentru pachete UDP
     */
    private void listen() {
        byte[] buffer = new byte[1024]; // sets buffer size

        while (running) {
            try {
                // while program is running, receive & handle UDP packets, otherwise exit
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length); // create UDP packet
                socket.receive(packet); // receive UDP packet from broadcast

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
     * Tratarea mesajului de status UDP
     */
    private void handleStatusMessage(String jsonStr) {
        try {
            // Parsing the JSON message
            JSONObject msg = new JSONObject(jsonStr);

            // Check status type
            if (!"status".equals(msg.getString("type"))) {
                return;
            }

            // Handle status message based on its type
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

            // If not null, the formatted string will be processed into one single message and sent to the UI
            if (formatted != null) {
                final String message = formatted;
                Platform.runLater(() -> {
                    if (statusHandler != null) {
                        statusHandler.accept(message); // hence we have an accept
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
