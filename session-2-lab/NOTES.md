What happens when temperature is changed from 0.2 to 1.0?
-- At 0.2 the answer is more focused and deterministic.
-- At 1.0 the answer is more creative and diverse.
Why should an application not retry every API error?
-- Retrying is only effective for transient errors like rate limits or temporary network issues. Retrying on terminal errors like invalid requests or configuration issues will not fix the problem and will only waste time.
Why should the API key not be stored directly in the source code?
-- It is a security risk because it can be exposed to unauthorized users. 
Why does conversation history increase token usage?
-- Conversation history is sent to the model with every request, so as the conversation grows longer, the token usage increases.
What is the main advantage of streaming?
-- Streaming allows the user to see the response as it is being generated, which can improve the user experience.
If 10,000 users use your application, what engineering problems might appear?
-- API rate limits, high API consumption costs, security risks, concurrency/scaling bottlenecks, and session state management.