package main.java.org.acme;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

@Path("/ping")
public class GreetingResource {
    @GET
    public String ping() {
        return "pong";
    }
}
