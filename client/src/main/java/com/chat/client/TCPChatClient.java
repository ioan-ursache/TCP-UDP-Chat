package com.chat.client;

import javafx.application.Platform;
import java.io.*;
import java.net.Socket;
import java.util.function.Consumer;

/**
 * TCP Client pentru Chat Application
 * Gestionează conexiunea la server și schimbul de mesaje
 */
public class TCPChatClient {
    private Socket socket;
    private BufferedReader input;
    private PrintWriter output;
    private String username;
    private boolean connected = false;
    private Consumer<String> messageHandler;

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
            input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            output = new PrintWriter(socket.getOutputStream(), true);

            // Trimite username pentru handshake
            output.println(username);

            connected = true;
            System.out.println("[CLIENT] Conectat la server: " + host + ":" + port);

            // Start thread pentru primire mesaje
            Thread receiverThread = new Thread(this::receiveMessages);
            receiverThread.setDaemon(true);
            receiverThread.start();

            return true;

        } catch (IOException e) {
            System.err.println("[CLIENT] Eroare conectare: " + e.getMessage());
            return false;
        }
    }

    /**
     * Trimite mesaj la server
     * @param message - conținut mesaj
     */
    public void sendMessage(String message) {
        if (connected && output != null) {
            output.println(message);
        }
    }

    /**
     * Thread pentru primire mesaje de la server
     * Rulează continuu în background
     */
    private void receiveMessages() {
        try {
            String message;
            while (connected && (message = input.readLine()) != null) {
                final String msg = message;

                // Update UI pe JavaFX Application Thread
                Platform.runLater(() -> {
                    if (messageHandler != null) {
                        messageHandler.accept(msg);
                    }
                });
            }
        } catch (IOException e) {
            if (connected) {
                System.err.println("[CLIENT] Conexiune pierdută: " + e.getMessage());
                disconnect();
            }
        }
    }

    /**
     * Deconectare de la server
     */
    public void disconnect() {
        connected = false;

        try {
            if (output != null) output.close();
            if (input != null) input.close();
            if (socket != null) socket.close();

            System.out.println("[CLIENT] Deconectat de la server");

        } catch (IOException e) {
            System.err.println("[CLIENT] Eroare la deconectare: " + e.getMessage());
        }
    }

    /**
     * Verifică dacă clientul este conectat
     * @return true dacă este conectat
     */
    public boolean isConnected() {
        return connected && socket != null && !socket.isClosed();
    }

    public String getUsername() {
        return username;
    }
}
