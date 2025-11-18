package com.chat.controller;

import com.chat.client.TCPChatClient;
import com.chat.client.UDPStatusListener;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.input.KeyCode;

/**
 * Controller pentru interfața JavaFX Chat
 * Integrează TCP (mesaje) și UDP (status)
 */
public class ChatController {

    @FXML private TextArea chatArea;
    @FXML private TextField messageInput;
    @FXML private Button sendButton;
    @FXML private Label statusLabel;
    @FXML private TextField serverIpField;
    @FXML private TextField serverPortField;
    @FXML private TextField usernameField;
    @FXML private Button connectButton;

    private TCPChatClient client;
    private UDPStatusListener udpListener;

    private static final int UDP_PORT = 5001;

    /**
     * Inițializare controller
     */
    @FXML
    public void initialize() {
        // Disable chat controls până la conectare
        messageInput.setDisable(true);
        sendButton.setDisable(true);
        chatArea.setEditable(false);

        // Default values
        serverIpField.setText("localhost");
        serverPortField.setText("5000");

        // Setup event handlers
        sendButton.setOnAction(e -> sendMessage());
        connectButton.setOnAction(e -> toggleConnection());

        // Trimite mesaj cu Enter
        messageInput.setOnKeyPressed(e -> {
            if (e.getCode() == KeyCode.ENTER) {
                sendMessage();
            }
        });

        // Send typing indicator when user types
        messageInput.textProperty().addListener((obs, oldVal, newVal) -> {
            if (client != null && client.isConnected() && !newVal.isEmpty()) {
                client.sendTypingIndicator();
            }
        });

        updateStatus("Deconectat", false);
    }

    /**
     * Toggle connection to server
     */
    @FXML
    private void toggleConnection() {
        if (client == null || !client.isConnected()) {
            connectToServer();
        } else {
            disconnectFromServer();
        }
    }

    /**
     * Connect to server
     */
    private void connectToServer() {
        String host = serverIpField.getText().trim();
        String portStr = serverPortField.getText().trim();
        String username = usernameField.getText().trim();

        // Validate input
        if (username.isEmpty()) {
            showAlert("Eroare", "Introduceți un username!");
            return;
        }

        if (host.isEmpty()) {
            showAlert("Eroare", "Introduceți adresa serverului!");
            return;
        }

        try {
            int port = Integer.parseInt(portStr);

            // Create TCP client
            client = new TCPChatClient(this::handleTCPMessage);

            if (client.connect(host, port, username)) {
                // Start UDP listener
                udpListener = new UDPStatusListener(UDP_PORT, this::handleUDPStatus);
                if (udpListener.start()) {
                    chatArea.appendText("[UDP] Status listener started\n");
                }

                // Update UI
                updateStatus("Conectat ca " + username, true);
                chatArea.appendText("=== Conectat la " + host + ":" + port + " ===\n");

                // Disable connection fields
                serverIpField.setDisable(true);
                serverPortField.setDisable(true);
                usernameField.setDisable(true);
                connectButton.setText("Deconectare");

                // Enable chat
                messageInput.setDisable(false);
                sendButton.setDisable(false);
                messageInput.requestFocus();

            } else {
                showAlert("Eroare", "Nu s-a putut conecta la server!\nVerificați că serverul rulează.");
            }

        } catch (NumberFormatException ex) {
            showAlert("Eroare", "Port invalid!");
        }
    }

    /**
     * Disconnect from server
     */
    private void disconnectFromServer() {
        // Stop UDP listener
        if (udpListener != null && udpListener.isRunning()) {
            udpListener.stop();
        }

        // Disconnect TCP
        if (client != null) {
            client.disconnect();
        }

        // Update UI
        updateStatus("Deconectat", false);
        chatArea.appendText("=== Deconectat de la server ===\n");

        // Enable connection fields
        serverIpField.setDisable(false);
        serverPortField.setDisable(false);
        usernameField.setDisable(false);
        connectButton.setText("Conectare");

        // Disable chat
        messageInput.setDisable(true);
        sendButton.setDisable(true);
    }

    /**
     * Trimite mesaj la server
     */
    @FXML
    private void sendMessage() {
        String message = messageInput.getText().trim();

        if (message.isEmpty()) {
            return;
        }

        if (client == null || !client.isConnected()) {
            showAlert("Eroare", "Nu sunteți conectat la server!");
            return;
        }

        // Handle commands
        if (message.startsWith("/")) {
            String cmd = message.substring(1).toLowerCase();
            if (cmd.equals("quit")) {
                disconnectFromServer();
                return;
            } else if (cmd.equals("list")) {
                client.sendCommand("list");
                messageInput.clear();
                return;
            }
        }

        // Send regular message
        client.sendMessage(message);

        // Display own message (echo)
        chatArea.appendText("You: " + message + "\n");
        messageInput.clear();
    }

    /**
     * Handler pentru mesaje TCP (chat, system)
     */
    private void handleTCPMessage(String message) {
        Platform.runLater(() -> {
            chatArea.appendText(message + "\n");
        });
    }

    /**
     * Handler pentru status UDP (join, leave, typing, presence)
     */
    private void handleUDPStatus(String statusMessage) {
        Platform.runLater(() -> {
            chatArea.appendText(statusMessage + "\n");
        });
    }

    /**
     * Update status label
     */
    private void updateStatus(String text, boolean connected) {
        Platform.runLater(() -> {
            statusLabel.setText(text);
            statusLabel.setStyle(connected ?
                "-fx-text-fill: green;" :
                "-fx-text-fill: red;");
        });
    }

    /**
     * Show alert dialog
     */
    private void showAlert(String title, String content) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }

    /**
     * Cleanup la închiderea aplicației
     */
    public void shutdown() {
        if (udpListener != null && udpListener.isRunning()) {
            udpListener.stop();
        }
        if (client != null && client.isConnected()) {
            client.disconnect();
        }
    }
}
