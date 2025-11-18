package com.chat.controller;

import com.chat.client.TCPChatClient;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.input.KeyCode;
import org.json.JSONObject;

/**
 * Controller pentru interfața JavaFX Chat
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

    /**
     * Inițializare controller
     * Apelat automat de JavaFX după încărcarea FXML
     */
    @FXML
    public void initialize() {
        // Disable chat controls până la conectare
        messageInput.setDisable(true);
        sendButton.setDisable(true);
        chatArea.setEditable(false);

        // Default values
        serverIpField.setText("localhost");
        serverPortField.setText("8080");

        // Setup event handlers
        sendButton.setOnAction(e -> sendMessage());
        connectButton.setOnAction(e -> toggleConnection());

        // Trimite mesaj cu Enter
        messageInput.setOnKeyPressed(e -> {
            if (e.getCode() == KeyCode.ENTER) {
                sendMessage();
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
            // Connect
            String host = serverIpField.getText().trim();
            String portStr = serverPortField.getText().trim();
            String username = usernameField.getText().trim();

            if (username.isEmpty()) {
                showAlert("Eroare", "Introduceți un username!");
                return;
            }

            try {
                int port = Integer.parseInt(portStr);

                // Create client cu message handler
                client = new TCPChatClient(this::handleReceivedMessage);

                if (client.connect(host, port, username)) {
                    updateStatus("Conectat ca " + username, true);
                    chatArea.appendText("=== Conectat la server " + host + ":" + port + " ===\n");

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
                    showAlert("Eroare", "Nu s-a putut conecta la server!");
                }

            } catch (NumberFormatException ex) {
                showAlert("Eroare", "Port invalid!");
            }

        } else {
            // Disconnect
            client.disconnect();
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
    }

    /**
     * Trimite mesaj la server
     */
    @FXML
    private void sendMessage() {
        String message = messageInput.getText().trim();

        if (!message.isEmpty() && client != null && client.isConnected()) {
            client.sendMessage(message);
            messageInput.clear();
        }
    }

    /**
     * Handler pentru mesaje primite de la server
     * @param jsonMessage - mesaj în format JSON
     */
    private void handleReceivedMessage(String jsonMessage) {
        try {
            // Parse JSON
            JSONObject json = new JSONObject(jsonMessage);
            String type = json.getString("type");
            String user = json.getString("user");
            String content = json.getString("content");

            // Format message
            String displayMessage;
            if ("system".equals(type)) {
                displayMessage = "[SYSTEM] " + content + "\n";
            } else {
                displayMessage = user + ": " + content + "\n";
            }

            // Update chat area
            Platform.runLater(() -> chatArea.appendText(displayMessage));

        } catch (Exception e) {
            // Fallback pentru mesaje non-JSON
            Platform.runLater(() -> chatArea.appendText(jsonMessage + "\n"));
        }
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
        if (client != null && client.isConnected()) {
            client.disconnect();
        }
    }
}
