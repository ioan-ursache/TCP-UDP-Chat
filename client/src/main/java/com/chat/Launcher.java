package com.chat;

import javafx.application.Application;

/**
 * Launcher entry point to start JavaFX app without triggering
 * the "JavaFX runtime components are missing" error when
 * running the Application subclass directly - error encountered
 */
public class Launcher {
    public static void main(String[] args) {
        Application.launch(ChatApp.class, args);
    }
}
