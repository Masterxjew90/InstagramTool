# InstagramTool
InstagramBot
Key Features:

    Login and Authentication:
        The user inputs their Instagram username and password, and the app logs in using the instagrapi.Client.

    Post Scheduling:
        Users can select an image/video and provide a title for the post.
        A QDateTimeEdit allows users to select a date and time to schedule the post.
        The post is scheduled using the APScheduler library, which runs the post_media function at the specified time.

    Scheduled Post Management:
        A dialog shows the list of scheduled posts with their details.
        Right-clicking on a scheduled post allows users to remove or edit it.

    Auto Message Checking:
        A background task checks for new likes and comments on the user’s posts every 5 minutes.
        The bot automatically sends a message to users who like the post and replies to comments.

    Error Handling:
        The login process, post scheduling, and auto-message checking are all wrapped with error handling to display appropriate messages when something goes wrong.

Points of Interest:

    Custom Context Menu: Right-clicking on a scheduled post shows a context menu allowing users to remove the post.
    Dynamic UI Changes: The UI changes dynamically after login—hiding login elements and showing post scheduling elements.
    Scheduled Post Handling: Posts are scheduled with the APScheduler, and duplicate posts are avoided. Existing scheduled posts are checked when scheduling a new one.
    Auto Message Checker: Periodically checks likes and comments on the user's posts and sends messages accordingly.
