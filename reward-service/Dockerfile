FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

# Copy pom.xml
COPY pom.xml .

# Download dependencies
RUN mvn dependency:go-offline

# Copy source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Use a smaller base image for the final image
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy the built jar from the builder stage
COPY --from=builder /app/target/reward-service-1.0-SNAPSHOT.jar ./reward-service.jar

# Expose the application port
EXPOSE 8081

# Set environment variables
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Run the application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar reward-service.jar"] 