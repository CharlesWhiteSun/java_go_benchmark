# build stage using official maven image (contains mvn)
FROM maven:3.9.4-eclipse-temurin-21 AS build
WORKDIR /usr/src/app

COPY pom.xml .
COPY src ./src

# build quarkus application (JVM jar)
RUN mvn -B package -DskipTests

# runtime stage
FROM eclipse-temurin:21-jre
WORKDIR /app
# copy quarkus-app layout (if using quarkus-maven-plugin)
COPY --from=build /usr/src/app/target/quarkus-app/ /app/
CMD ["java", "-jar", "/app/quarkus-run.jar"]
