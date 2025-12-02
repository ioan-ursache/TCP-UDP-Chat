Distributed Chat Client — How to run Launcher from the command line

This project is a Java 17 + JavaFX client. The entry point for the UI is the class:

- src\main\java\com\chat\Launcher.java (main class: com.chat.Launcher)

The simplest and most reliable way to run it from the command line is to use the Maven Wrapper that is already included in the project. The JavaFX Maven Plugin will set up the correct JavaFX modules for your OS automatically.

Prerequisites
- JDK 17 installed and on PATH (java -version should report 17.x)

Quick start (Windows PowerShell or CMD)
1) Open a terminal in the project root:
   C:\Users\ursac\IdeaProjects\TCP-UDP-Chat\client
2) Run the JavaFX app via Maven Wrapper:
   .\mvnw.cmd clean javafx:run

That’s it. The application window should open. The configured main class is com.chat.Launcher (see pom.xml -> javafx-maven-plugin).

Alternative: run the compiled classes with dependencies on the classpath
If you prefer to run java directly (without the JavaFX Maven Plugin), you must place the JavaFX libraries and other dependencies on the classpath and enable the JavaFX modules. You can let Maven build the runtime classpath for you, then call java yourself.

Steps (Windows PowerShell):
1) From the project root, compile classes:
   .\mvnw.cmd -q -DskipTests package
2) Generate a runtime classpath file (cp.txt):
   .\mvnw.cmd -q -DincludeScope=runtime -DskipTests dependency:build-classpath -Dmdep.outputFile=cp.txt
3) Run the app specifying modules and classpath:
   $cp = Get-Content cp.txt
   java --add-modules=javafx.controls,javafx.fxml -cp "target\classes;$cp" com.chat.Launcher

Note: Because this project uses the Java Module System (see src\main\java\module-info.java with module name com.chat.client), running via the JavaFX Maven Plugin is recommended—it handles the platform-specific JavaFX artifacts for you.

Optional: Create a runnable (shaded) JAR
This project is configured with the Maven Shade Plugin. After packaging, you should find a shaded JAR in the target directory that includes dependencies.

Build:
  .\mvnw.cmd -q -DskipTests package

Run (the exact file name may include “-shaded”):
  java -jar .\target\distributed-chat-client-1.0-MVP-shaded.jar

If you encounter issues running the shaded JAR on your platform, use the first method (mvn javafx:run), which is platform-aware for JavaFX.

Troubleshooting
- If you see “JavaFX runtime components are missing”: run via .\mvnw.cmd javafx:run or ensure you added the JavaFX modules and libraries to the classpath when using java directly.
- JAVA_HOME not set: The Maven Wrapper (mvnw.cmd) in this project will try to use the 'java' found on your PATH automatically. If neither JAVA_HOME is set nor 'java' is on PATH, set JAVA_HOME to your JDK 17 installation (e.g., C:\Program Files\Java\jdk-17) or add its bin folder to PATH. Ensure it’s a JDK 17, not a JRE.
