package com.example.whatsapp.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@RestController
public class WebhookController {

    private static final String AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2";

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    // --- In-memory State Tracking ---
    private static final Map<String, String> userState = new ConcurrentHashMap<>();
    private static final Map<String, Map<String, String>> userData = new ConcurrentHashMap<>();

    // State Constants
    private static final String STATE_START = "START";
    private static final String STATE_MENU = "MENU";
    private static final String STATE_ASK_NAME = "ASK_NAME";
    private static final String STATE_ASK_ADDRESS = "ASK_ADDRESS";
    private static final String STATE_COMPLETED = "COMPLETED";

    // ---------------------------------------------------------------
    // GET endpoint — verification / health check
    // ---------------------------------------------------------------
    @GetMapping("/messages/whatsapp")
    public String testWebhook(@RequestParam(value = "hub.challenge", required = false) String challenge) {
        if (challenge != null)
            return challenge;
        return "Webhook working";
    }

    // ---------------------------------------------------------------
    // POST endpoint — main webhook handler
    // ---------------------------------------------------------------
    @PostMapping("/messages/whatsapp")
    public Map<String, String> receiveMessage(@RequestBody JsonNode body) {

        // Log full incoming payload
        System.out.println("=== Incoming Webhook Payload ===");
        System.out.println(body.toPrettyString());
        System.out.println("================================");

        // --- Navigate to nested structure: body → data → message ---
        JsonNode messageNode = body.path("data").path("message");

        // Extract phone_number
        String phoneNumber = messageNode.has("phone_number")
                ? messageNode.get("phone_number").asText().trim()
                : "Not present";

        // Extract message_content.text
        String messageText = "Not present";
        if (messageNode.has("message_content") && messageNode.get("message_content").has("text")) {
            messageText = messageNode.get("message_content").get("text").asText().trim();
        }

        // Extract userName
        String senderName = messageNode.has("userName")
                ? messageNode.get("userName").asText().trim()
                : "Unknown";

        // Log extracted values
        System.out.println("[Extracted] Phone   : " + phoneNumber);
        System.out.println("[Extracted] Message : " + messageText);
        System.out.println("[Extracted] Sender  : " + senderName);

        if (phoneNumber.equals("Not present")) {
            return Map.of("status", "error", "message", "Phone number missing");
        }

        // --- Chatbot Logic (State Machine) ---
        String currentState = userState.getOrDefault(phoneNumber, STATE_START);
        System.out.println("[Chatbot] Current State for " + phoneNumber + ": " + currentState);

        String replyText = "";
        String nextState = currentState;

        // Reset flow if "Hi" or similar or if in COMPLETED state
        if (messageText.equalsIgnoreCase("Hi") || messageText.equalsIgnoreCase("Hello") || currentState.equals(STATE_COMPLETED)) {
            replyText = "Welcome to Yotindia!\nReply:\n1 Order Product\n2 View Products";
            nextState = STATE_MENU;
            userData.remove(phoneNumber); // Clear old data
        } else {
            switch (currentState) {
                case STATE_MENU:
                    if (messageText.equals("1")) {
                        replyText = "Enter your name:";
                        nextState = STATE_ASK_NAME;
                    } else if (messageText.equals("2")) {
                        replyText = "Available products: Leather Bag";
                        nextState = STATE_MENU;
                    } else {
                        replyText = "Please reply with 1 or 2";
                    }
                    break;

                case STATE_ASK_NAME:
                    userData.computeIfAbsent(phoneNumber, k -> new HashMap<>()).put("name", messageText);
                    replyText = "Enter your address:";
                    nextState = STATE_ASK_ADDRESS;
                    break;

                case STATE_ASK_ADDRESS:
                    userData.getOrDefault(phoneNumber, new HashMap<>()).put("address", messageText);
                    replyText = "Order confirmed!\nThank you for ordering.";
                    nextState = STATE_COMPLETED;
                    break;

                default:
                    replyText = "Welcome to Yotindia!\nReply:\n1 Order Product\n2 View Products";
                    nextState = STATE_MENU;
                    break;
            }
        }

        userState.put(phoneNumber, nextState);
        System.out.println("[Chatbot] Reply    : " + replyText);
        System.out.println("[Chatbot] Next State: " + nextState);

        // --- Send AiSensy Template Reply ---
        sendAiSensyReply(phoneNumber, senderName);

        // Return acknowledgement
        Map<String, String> response = new HashMap<>();
        response.put("status", "received");
        response.put("phone", phoneNumber);
        response.put("state", nextState);

        return response;
    }

    // ---------------------------------------------------------------
    // AiSensy Send Message
    // ---------------------------------------------------------------
    private void sendAiSensyReply(String phoneNumber, String senderName) {

        // Guard: skip if phone number is missing
        if (phoneNumber == null || phoneNumber.isBlank() || phoneNumber.equals("Not present")) {
            System.out.println("[AiSensy] Skipping reply — phone number is missing.");
            return;
        }

        // Guard: skip if API key is not configured
        String apiKey = System.getenv("AISENSY_API_KEY");
        System.out.println("[AiSensy] API Key check: " + (apiKey == null ? "MISSING" : "PRESENT"));
        
        if (apiKey == null || apiKey.isBlank()) {
            System.out.println("[AiSensy] Skipping reply — AISENSY_API_KEY env variable is not set.");
            return;
        }

        try {
            // Build payload for Campaign API
            Map<String, Object> payload = new HashMap<>();
            payload.put("apiKey", apiKey);
            payload.put("campaignName", "Greetings");
            payload.put("destination", phoneNumber);
            payload.put("userName", senderName);
            
            // Per requirement: template has NO variables (use empty map)
            payload.put("templateParams", new HashMap<>());

            System.out.println("[AiSensy] Payload: " + payload);

            // Set headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);

            // POST to AiSensy Campaign API
            ResponseEntity<String> apiResponse = restTemplate.exchange(
                    AISENSY_API_URL,
                    HttpMethod.POST,
                    request,
                    String.class
            );

            System.out.println("[AiSensy] Response status: " + apiResponse.getStatusCode());
            System.out.println("[AiSensy] Response body: " + apiResponse.getBody());

        } catch (Exception e) {
            // Log error but do NOT crash — webhook must always return 200
            System.err.println("[AiSensy] Failed to send reply: " + e.getMessage());
        }
    }
}
