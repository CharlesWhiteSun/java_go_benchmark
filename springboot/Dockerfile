# build stage using official maven image (contains mvn)
FROM maven:3.9.4-eclipse-temurin-21 AS build
WORKDIR /app

# copy only what we need first for caching
COPY pom.xml .
COPY src ./src

# build the jar
RUN mvn -B package -DskipTests

# runtime stage
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","app.jar"]
