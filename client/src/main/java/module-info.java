module com.chat.client {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.graphics;
    requires org.json;


    opens com.chat.client to javafx.fxml;
    opens com.chat.controller to javafx.fxml;
    // Export the Application package so JavaFX launcher (javafx.graphics) can access ChatApp
    exports com.chat to javafx.graphics;
    exports com.chat.client;
}