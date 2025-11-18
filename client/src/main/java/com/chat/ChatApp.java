package com.chat;

import com.chat.controller.ChatController;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

/**
 * Main JavaFX Application pentru Chat Client
 */
public class ChatApp extends Application {

    private ChatController controller;

    @Override
    public void start(Stage primaryStage) throws Exception {
        // Load FXML
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/chat.fxml"));
        Parent root = loader.load();
        controller = loader.getController();

        // Setup scene
        Scene scene = new Scene(root, 500, 600);

        // Setup stage
        primaryStage.setTitle("TCP Chat Client - Distributed Chat Application");
        primaryStage.setScene(scene);
        primaryStage.setMinWidth(450);
        primaryStage.setMinHeight(500);

        // Handle window close
        primaryStage.setOnCloseRequest(e -> {
            if (controller != null) {
                controller.shutdown();
            }
        });

        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
