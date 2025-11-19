package com.chat.client;

import javafx.application.Platform;
import org.json.JSONObject;

import java.io.*;
import java.net.Socket;
import java.util.function.Consumer;

/**
 * TCP Client pentru Chat Application
 * Implementează protocolul TCP-UDP cu mesaje JSON
 */
public class TCPChatClient {
    private Socket socket;
    private BufferedReader input;
    private PrintWriter output;
    private String username;
    private boolean connected = false;
    private Consumer<String> messageHandler;
    private Thread receiverThread;

    /**
     * Constructor
     * @param messageHandler - callback pentru procesare mesaje primite
     */
    public TCPChatClient(Consumer<String> messageHandler) {
        this.messageHandler = messageHandler;
    }

    /**
     * Conectare la server
     * @param host - adresa IP server
     * @param port - port server
     * @param username - nume utilizator
     * @return true dacă conexiunea reușește
     */
    public boolean connect(String host, int port, String username) {
        try {
            this.username = username;
            socket = new Socket(host, port);

            // Setup I/O streams
            input = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF-8"));
            output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF-8"), true);

            connected = true;
            System.out.println("[CLIENT] Connected to " + host + ":" + port);

            // Send LOGIN message according to protocol
            JSONObject loginMsg = new JSONObject();
            loginMsg.put("type", "login");
            loginMsg.put("username", username);
            output.println(loginMsg.toString());
            System.out.println("[CLIENT] Sent login: " + loginMsg.toString());

            // Start receiver thread
            receiverThread = new Thread(this::receiveMessages);
            receiverThread.setDaemon(true);
            receiverThread.start();

            return true;

        } catch (IOException e) {
            System.err.println("[CLIENT] Connection error: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Trimite mesaj de chat la server
     * @param text - conținut mesaj
     */
    public void sendMessage(String text) {
        if (!connected || output == null) {
            System.err.println("[CLIENT] Not connected!");
            return;
        }

        try {
            // Create MESSAGE according to protocol
            JSONObject msg = new JSONObject();
            msg.put("type", "message");
            msg.put("from", username);
            msg.put("text", text);

            String jsonStr = msg.toString();
            output.println(jsonStr);
            System.out.println("[CLIENT] Sent: " + jsonStr);

        } catch (Exception e) {
            System.err.println("[CLIENT] Send error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Trimite comandă la server
     * @param command - comandă (ex: "quit", "list")
     */
    public void sendCommand(String command) {
        if (!connected || output == null) {
            return;
        }

        try {
            JSONObject msg = new JSONObject();
            msg.put("type", "command");
            msg.put("cmd", command);
            msg.put("args", new String[]{});

            output.println(msg.toString());
            System.out.println("[CLIENT] Sent command: " + command);

        } catch (Exception e) {
            System.err.println("[CLIENT] Command error: " + e.getMessage());
        }
    }

    /**
     * Trimite indicator de scriere
     */
    public void sendTypingIndicator() {
        if (!connected || output == null) {
            return;
        }

        try {
            JSONObject msg = new JSONObject();
            msg.put("type", "message");
            msg.put("from", username);
            msg.put("text", "_typing_");

            output.println(msg.toString());

        } catch (Exception e) {
            // Ignore typing indicator errors
        }
    }

    /**
     * Thread pentru primire mesaje de la server
     */
    private void receiveMessages() {
        try {
            String line;
            while (connected && (line = input.readLine()) != null) {
                final String message = line;
                System.out.println("[CLIENT] Received: " + message);

                // Parse and format message
                String formatted = formatMessage(message);

                // Update UI on JavaFX thread
                Platform.runLater(() -> {
                    if (messageHandler != null) {
                        messageHandler.accept(formatted);
                    }
                });
            }
        } catch (IOException e) {
            if (connected) {
                System.err.println("[CLIENT] Connection lost: " + e.getMessage());
                disconnect();
            }
        }
    }

    /**
     * Formatează mesajul JSON pentru afișare
     */
    private String formatMessage(String jsonStr) {
        try {
            JSONObject msg = new JSONObject(jsonStr);
            String type = msg.getString("type");

            switch (type) {
                case "system":
                    return "[SYSTEM] " + msg.getString("text");

                case "message":
                    String from = msg.getString("from");
                    String text = msg.getString("text");
                    return from + ": " + text;

                default:
                    return jsonStr;
            }

        } catch (Exception e) {
            // If not valid JSON, return as-is
            return jsonStr;
        }
    }

    /**
     * Deconectare de la server
     */
    public void disconnect() {
        if (!connected) {
            return;
        }

        connected = false;

        try {
            // Send quit command
            if (output != null) {
                sendCommand("quit");
            }

            // Close streams
            if (output != null) output.close();
            if (input != null) input.close();
            if (socket != null) socket.close();

            System.out.println("[CLIENT] Disconnected");

        } catch (IOException e) {
            System.err.println("[CLIENT] Disconnect error: " + e.getMessage());
        }
    }

    /**
     * Verifică dacă clientul este conectat
     */
    public boolean isConnected() {
        return connected && socket != null && !socket.isClosed();
    }

    public String getUsername() {
        return username;
    }
}
