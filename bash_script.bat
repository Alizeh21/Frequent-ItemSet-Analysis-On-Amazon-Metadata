@echo off
SET KAFKA_DIR=D:\kafka_2.13-3.7.0
SET PROJECT_DIR=D:\Asst-3

echo Starting Zookeeper...
start "Zookeeper" cmd /k "%KAFKA_DIR%\bin\windows\zookeeper-server-start.bat %KAFKA_DIR%\config\zookeeper.properties"
timeout /T 20 /NOBREAK

echo Starting Kafka server...
start "Kafka" cmd /k "%KAFKA_DIR%\bin\windows\kafka-server-start.bat %KAFKA_DIR%\config\server.properties"
timeout /T 20 /NOBREAK

echo Running Producer Python script...
start "Producer" cmd /k "cd %PROJECT_DIR% && python producer.py"

echo Running Consumer 1 Python script...
start "Consumer" cmd /k "cd %PROJECT_DIR% && python consumer(PCY).py"

echo Running Consumer 2 Python script...
start "Consumer" cmd /k "cd %PROJECT_DIR% && python consumer(Apriori).py"

@REM echo Running Consumer 3 Python script...
@REM start "Consumer" cmd /k "cd %PROJECT_DIR% && python consumer (PCY).py"

echo All services started.
echo To stop services, close the command windows or use Ctrl+C in each one.
