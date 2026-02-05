REST API
Your domain's API key is available in the Developers section of the Daily dashboard.

Domain owners can view and regenerate your team's API key.

Members do not have access to your team's API key.

Need a staging key? Learn more here.

If you're a member and you require access, request the key from a team member or request administrator privileges from one of your team's admins.

HTTPS is required for all Daily REST API requests.
Authentication

The Daily API uses API keys to authenticate requests.

Almost all of the Daily API endpoints require that you include your API key in the Authorization header of your HTTPS request. For example:

cURL
Copy to clipboard
curl --request GET \
  --url https://api.daily.co/v1/rooms \
  --header "Authorization: Bearer DAILY_API_KEY"

Each API key is tied to a specific Daily domain.

You should keep your API key secret. Never use the API key in client-side web browser code, for example.

If an API call requires authentication, but no Authorization: Bearer header is present, we return an HTTP 400 error, with a body that includes an error parameter set to the string "authorization-header-error".

If an API call requires authentication but the API key provided in the authorization header isn't valid, we return an HTTP 401 error, with a body that includes an error parameter set to the string "authentication-error".

Rate limits

Daily uses rate limiting to ensure the stability of the API across all of Daily's users. If you make lots of requests in succession, you may see 429 status codes returned by the API. Daily has two levels of rate limiting, each of which affect different endpoints.

For most of our API endpoints, you can expect a limit of 20 requests per second, or 100 requests over a 5 second window.
For the DELETE /rooms/:name and GET /recordings endpoints, you can expect about 2 requests per second, or 50 requests over a 30 second window.
For starting a Recording, Livestreaming, PSTN, and SIP call, you can expect about 1 requests per second, or 5 requests over a 5 second window. For example, you can start a recording and initiate a PSTN dial-out immediately when the first participant joins a call, so it is possible to do a burst of requests as long as you are within the 5 requests in that 5 second window.
You should attempt to retry 429 status codes in order to handle limiting gracefully. A good technique to apply here is to retry your requests with an exponential backoff schedule to help reduce your request volume over each window. Many HTTP clients offer this as a configuration option out of the box.

In order to ensure stability and prevent abuse, we may alter the stated limits. Contact support if you need to increase your API limits.

Errors

The Daily API endpoints all return errors, wherever possible, as HTTP 4xx or 5xx error responses.

Error response bodies generally includes two parameters: error, and info. The error parameter is a string indicating an error type, and the info parameter fills in a bit more human readable information, wherever available.

The error types are stable; we don't expect to change them (though we'll likely add new error types over time.) But please treat the info strings only as additional information you use while developing and debugging. Content of the info parameter is not fixed and may change as we improve error feedback.

JSON
Copy to clipboard
// Example: an error response body
{
  "error": "invalid-request-error",
  "info": "bad Authorization header format"
}

HTTP status codes

HTTP status code	Response	Interpretation
200	OK	Everything worked as expected.
400	Bad Request	The operation could not be performed as requested.
401	Unauthorized	The provided API key was not valid.
403	Forbidden	The API key was valid but the requested resource was forbidden.
404	Not Found	The requested REST resource did not exist.
429	Too Many Requests	Too many requests were sent in too short a period of time. Please throttle your request rate.
5xx	Server Errors	Something unexpected happened on the server side. Please ping us to report this, if possible.
Error types

Error string	Description
authentication-error	The API key is not valid.
authorization-header-error	The Authorization header is missing or badly formatted.
forbidden-error	The API key is valid but the requested resource is forbidden.
json-parsing-error	The JSON request body could not be parsed.
invalid-request-error	The request could not be performed. More information is usually available in the info field of the response body. Typical causes are missing required parameters, bad parameter values, etc.
rate-limit-error	Too many requests were sent in too short a period of time. Please throttle your request rate.
server-error	Something unexpected went wrong.
Pagination

Fetching 100 results at a time

The list rooms and list recordings API endpoints return a maximum of 100 data objects at one time, and accept pagination arguments in their query strings.

All pagination arguments are optional. Without any pagination arguments, the list methods return up to 100 data objects, sorted in reverse chronological order by creation time. (In other words, by default, you just get back a list of your most recently created room or recording objects!)

It's helpful to think of pagination arguments — as the name suggests — in terms of defining "pages" of results.

The limit argument sets the size of the page (how many objects each page contains), and defaults to a value of 100.
The starting_after argument sets the starting point of the page and is used to fetch "subsequent" pages of results – as if you were paging through a book from front to back.
The ending_before argument is the opposite, and is used to fetch previous pages of results -- as if you were paging through a book from back to front.
A special ending_before argument, OLDEST, is available to facilitate fetching pages of results "backwards," from oldest objects to newest.
Note that the granularity for created_at timestamps is one second. The returned list order is stable, because id is the secondary sort field. But if you create multiple rooms within a 1-second window, the list order may not be precisely reverse-chronological.

Pagination argument	Description
limit	A limit on the number of objects to be returned. Maximum value is 100. Default value (if not supplied) is 100.
starting_after	An object ID to be used as a pagination cursor. The first object returned will be the object immediately after the object this id. This argument is commonly used to fetch the "next" page of results.
ending_before	The opposite of starting_after. The last page of returned results will be the object immediately preceding the object with this id. The special value OLDEST fetches the "last" page of results (the page containing the objects created longest ago).
Examples

cURL
Copy to clipboard
# list your five most recently created rooms
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer DAILY_API_KEY" \
     https://api.daily.co/v1/rooms?limit=5

 # data[0] is your most recently created room

 # if you have at least five rooms,
 # data[4] is your fifth-newest room

cURL
Copy to clipboard
# list your five oldest rooms
curl -H "Content-Type: application/json" \
    -H "Authorization: Bearer DAILY_API_KEY" \
    https://api.daily.co/v1/rooms?limit=5&ending_before=OLDEST

# data[data.length-1] is your oldest room

# if you have at least five rooms,
# data[0] is your fifth-oldest room

Pseudocode for fetching until there are no more results available

Here's what code looks like that fetches and does something will all of your room objects. We've left error checking as an exercise for the reader.

JavaScript
Copy to clipboard
// fetch all rooms// get first page of results
let rooms = getPageOfRooms({
  endpoint: 'https://api.daily.co/v1/rooms',
});

while (rooms.data.length > 0) {
  // do something with each room object
  for (var i = 0; i < rooms.data.length; i++) {
    doSomeStuff(rooms.data[i]);
  }

  // fetch another page
  rooms = getPageOfRooms({
    endpoint:
      'https://api.daily.co/v1/rooms?starting_after=' +
      rooms.data[rooms.data.length - 1].id,
  });
}
your-domain.daily.co
Your Daily domain

Your domain is your top-level object in the Daily API.

You create a Daily domain when you sign up for a Daily account. Once you have a domain, you can create Daily room URLs to host video calls.

JSON
Copy to clipboard
{
  "domain_name": "your-domain",
  "config": {
    "hide_daily_branding": false,
    "redirect_on_meeting_exit": "https://your-domain.co/vid-exit",
    "hipaa": false,
    "intercom_auto_record": false,
    "lang": "en"
  }
}
You can use the Daily REST API to retrieve information about your domain and set domain configuration options, like the default language of the rooms on your domain.

Configuration
enable_advanced_chat
boolean
Property that gives end users a richer chat experience. This includes:

Emoji reactions to chat messages
Emoji picker in the chat input form
Ability to send a Giphy chat message
⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_people_ui
boolean
Determines if Daily Prebuilt displays the People UI. When set to true, a People button in the call tray reveals a People tab in the call sidebar. The tab lists all participants, and next to each name indicates audio status and an option to pin the participant. When enable_people_ui is set to false, the button and tab are hidden.

⚠️ Has no effect on custom calls built on the Daily call object.
Default: true
enable_cpu_warning_notifications
boolean
Determines if Daily Prebuilt displays CPU warning notifications. When set to true, snackbar notifications appear when high CPU usage is detected. When set to false, these notifications are hidden.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: true
enable_pip_ui
boolean
Sets whether rooms for this domain can use Daily Prebuilt's Picture in Picture controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle the Picture in Picture feature.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_emoji_reactions
boolean
Determines if Daily Prebuilt displays the Emoji Reactions UI. When set to true, a Reactions button appears in the call tray. This button allows users to select and send a reaction into the call. When set to false, the Reactions button is hidden and the feature is disabled.

Usage: This feature is a good fit for meetings when a host or presenter would benefit from receiving nonverbal cues from the audience. It's also great to keep meetings fun.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_hand_raising
boolean
Sets whether the participants in the room can use Daily Prebuilt's hand raising controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle a hand raise.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_prejoin_ui
boolean
Determines whether participants enter a waiting room with a camera, mic, and browser check before joining a call in any room under this domain.

⚠️ You must be using Daily Prebuilt to use enable_prejoin_ui.
Default: true
enable_breakout_rooms
boolean
Sets whether rooms for this domain have Daily Prebuilt’s breakout rooms feature enabled. When set to true, an owner in a Prebuilt call can create breakout rooms to divide participants into smaller, private groups.

⚠️ You must be using Daily Prebuilt to use enable_breakout_rooms.

⚠️ This property is in beta.
Default: false
enable_live_captions_ui
boolean
Sets whether participants in a room see a closed captions button in their Daily Prebuilt call tray. When the closed caption button is clicked, closed captions are displayed locally.

When set to true, a closed captions button appears in the call tray. When set to false, the closed captions button is hidden from the call tray.

Note: Transcription must be enabled for the room or users must have permission to start transcription for this feature to be enabled. View the transcription guide for more details.

⚠️ You must be using Daily Prebuilt to use enable_live_captions_ui.
Default: false
enable_network_ui
boolean
Determines whether the network button, and the network panel it reveals on click, appears across all rooms belonging to this domain.

⚠️ You must be using Daily Prebuilt to use enable_network_ui.
Default: false
enable_noise_cancellation_ui
boolean
Determines whether Daily Prebuilt displays noise cancellation controls. When set to true, a participant can enable microphone noise cancellation during a Daily Prebuilt call. ⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object. To learn more about adding noise cancellation to a custom application, see the updateInputSettings() docs.
Default: true
enable_video_processing_ui
boolean
Determines whether Daily Prebuilt displays background blur controls. When set to true, a participant can enable blur during a Daily Prebuilt call.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: true
hide_daily_branding
boolean
PAY-AS-YOU-GO
Whether "Powered by Daily" displays in the in-call UI.
Default: false
redirect_on_meeting_exit
string
(For meetings that open in a separate browser tab.) When a user clicks on the in-call menu bar's "leave meeting" button, the browser loads this URL. A query string that includes a parameter of the form recent-call=<domain>/<room> is appended to the URL. On mobile, you can redirect to a deep link to bring a user back into your app.
hipaa
boolean
PAID ADD-ON
Email us at help@daily.co to turn on HIPAA. Learn more about our HIPAA compliance.
Default: false
intercom_auto_record
boolean
Whether to automatically start recording when an Intercom support agent joins an Intercom-created call. Please see our Intercom Messenger App page for more information.

⚠️This method is read-only; please contact us if you'd like to enable intercom call auto-recording.
lang
string
The default language for the video call UI, for all calls.

If you set the language at this domain level, you can still override the setting for specific rooms in a room's configuration properties, or for a specific participant in a meeting token.

You can also set the language dynamically using the front-end library setDailyLang() method.

* Norwegian "no" and Russian "ru" are only available in the new Daily Prebuilt.
Options: "da","de","en","es","fi","fr","it","jp","ka","nl","no","pt","pt-BR","pl","ru","sv","tr","user"
Default: en
meeting_join_hook
string
Sets a URL that will receive a webhook when a user joins a room.

⚠️ In place of the meeting_join_hook, we recommend setting up a webhook and listening for the participant.joined event.
Default: NULL
geo
string
Daily uses signaling servers to manage all of the participants in a given call session. In an SFU/server mode call, the server will send and receive all audio and video from each participant. In a peer-to-peer call, each participant sends media directly to and from each other peer, but a signaling server still manages call state.

Daily runs servers in several different AWS regions to minimize latency for users around the world. The job of 'picking' a call server is handled when the first participant joins a room. The first participant's browser connects to a call server using Amazon's Route 53 DNS resolution, which chooses a server in the region closest to them.

This isn't always optimal. For example, if one person joins in London, and then ten more people join from Cape Town, the call will still be hosted out of eu-west-2 . The majority of the participants will have higher latency to the server than if one of them had joined first and the call was being hosted in af-south-1. In cases like this, you may want to configure your domain (or a specific room) to always choose a call server in a specific AWS region.

Available regions:

"af-south-1" (Cape Town)
"ap-northeast-2" (Seoul)
"ap-southeast-1" (Singapore)
"ap-southeast-2" (Sydney)
"ap-south-1" (Mumbai)
"eu-central-1" (Frankfurt)
"eu-west-2" (London)
"sa-east-1" (São Paulo)
"us-east-1" (N. Virginia)
"us-west-2" (Oregon)
Default: NULL
rtmp_geo
string
Used to select the region where an RTMP stream should originate. In cases where RTMP streaming services aren't available in the desired region, we'll attempt to fall back to the default region based on the SFU being used for the meeting.

Available regions:

"us-west-2" (Oregon)
"eu-central-1" (Frankfurt)
"ap-south-1" (Mumbai)
The default regions are grouped based on the SFU region like so:

RTMP region "us-west-2" includes SFU regions: "us-west-2", "us-east-1", "sa-east-1"
RTMP region "eu-central-1" includes SFU regions: "eu-central-1", "eu-west-2", "af-south-1"
RTMP region "ap-south-1" includes SFU regions: "ap-southeast-1", "ap-southeast-2", "ap-northeast-2", "ap-south-1"
Default: The closest available region to the SFU region used by the meeting.
disable_rtmp_geo_fallback
boolean
Disable the fall back behavior of rtmp_geo. When rtmp_geo is set, we first try to connect to a media server in desired region. If a media server is not available in the desired region, we fall back to default region based on SFU's region. This property disables this automatic fall back. When this property is set, we will trigger a recording/streaming error event when media worker is unavailable. Also, the client should retry recording/streaming.
Default: false
enable_terse_logging
boolean
Reduces the volume of log messages. This feature should be enabled when there are more than 200 participants in a meeting to help improve performance.

See our guides for supporting large experiences for additional instruction.
Default: false
enable_transcription_storage
boolean
Live transcriptions generated can be saved as WebVTT. This flag controls if transcription started with startTranscription() should be saved or not.
Default: false
transcription_bucket
object
Configures an S3 bucket in which to store transcriptions. See the S3 bucket guide for more information.
bucket_name
string
The name of the Amazon S3 bucket to use for transcription storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the transcription in the specified bucket.
allow_api_access
boolean
Whether the transcription should be accessible using Daily's API.
recordings_template
string
Cloud recordings are stored in either Daily's S3 bucket or the customer's own S3 bucket. By default recordings are stored as {domain_name}/{room_name}/{epoch_time}. Sometimes, the use case may call for custom recording file names to be used (for example, if you'd like to enforce the presence of the .mp4 extension in the file name).

recordings_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in milliseconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting recorded (optional)
mtg_session_id: The ID of the meeting session which is getting recorded (optional)
instance_id: The instance ID of the recording (optional)
recording_id: The recording ID of the recording (optional)
The restrictions for defining a recording template are as follows:

The epoch_time tag is mandatory to ensure the recording file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
.mp4 is the only valid extension
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.
transcription_template
string
transcriptions can be stored in either Daily's S3 bucket or the customer's own S3 bucket. By default transcriptions are stored as {domain_name}/{room_name}/{epoch_time}.vtt. Sometimes, the use case may call for custom file path to be used (for example, if you'd like to map stored transcription to mtgSessionId).

transcription_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in seconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting transcribed (optional)
mtg_session_id: The ID of the meeting session which is getting transcribed (optional)
instance_id: The instance ID of the transcription (optional)
transcript_id: The transcript ID of the transcription (optional)
The restrictions for defining a transcription template are as follows:

The epoch_time tag is mandatory to ensure the transcription file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.vtt.
enable_mesh_sfu
boolean
Configures a room to use multiple SFUs for a call's media. This feature enables calls to scale to large sizes and to reduce latency between participants. It is recommended specifically for interactive live streaming.

See our guide for interactive live streaming for additional instruction.
sfu_switchover
number
Dictates the participant count after which room topology automatically switches from Peer-to-Peer (P2P) to Selective Forwarding Unit (SFU) mode, or vice versa.

For example, if sfu_switchover is set to 2 and the current network topology is P2P, the topology will switch to SFU mode when the third participant joins the call. If the current topology is SFU, it will switch to P2P mode when the participant count decreases from 2 to 1.

We recommend specifying an integer value for this property except for cases where you would like the room to switch to SFU mode as soon as the first participant joins. In this case, set sfu_switchover to 0.5.

See our guide about video call architecture for additional information.
Default: 0.5
enable_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_adaptive_simulcast to true will enable Daily Adaptive Bitrate for 1:1 calls.
Default: true
enforce_unique_user_ids
boolean
Configures a domain or room to disallow multiple participants from having the same user_id. This feature can be enabled to prevent users from "sharing" meeting tokens. When enabled, a participant joining or reconnecting to a meeting will cause existing participants with the same user_id to be ejected.
Default: false
recordings_bucket
object
Configures an S3 bucket in which to store recordings. See the S3 bucket guide for more information.

Properties:
bucket_name
string
The name of the Amazon S3 bucket to use for recording storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the recording in the specified bucket.
allow_api_access
boolean
Controls whether the recording will be accessible using Daily's API.
allow_streaming_from_bucket
boolean
Specifies which Content-Disposition response header the recording link retrieved from the access-link REST API endpoint will have. If allow_streaming_from_bucket is false, the header will be Content-Dispostion: attachment. If allow_streaming_from_bucket is true, the header will be Content-Disposition: inline. To play the recording link directly in the browser or embed it in a video player, set this property to true.
Default: false
permissions
object
Specifies the initial default permissions for a non-meeting-owner participant joining a call.

Each permission (i.e. each of the properties listed below) can be configured in the meeting token, the room, and/or the domain, in decreasing order of precedence.

Participant admins (those with the 'participants' value in their canAdmin permission) can also change participants' permissions on the fly during a call using updateParticipant() or updateParticipants().
hasPresence
boolean
Whether the participant appears as "present" in the call, i.e. whether they appear in participants().
canSend
boolean | array
Which types of media a participant should be permitted to send.

Can be:

An Array containing any of 'video', 'audio', 'screenVideo', and 'screenAudio'
true (meaning "all")
false (meaning "none")
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
boolean | array
Which admin tasks a participant is permitted to do.

Can be:

An array containing any of 'participants', 'streaming', or 'transcription'
true (meaning "all")
false (meaning "none")
Default: { canSend: true, canReceive: { base: true }, hasPresence: true, canAdmin: false }
batch_processor_bucket
object
Defines a custom S3 bucket where the batch processor will write its output
enable_opus_fec
boolean
Enables the use of Opus in-band FEC (Forward Error Correction) when encoding audio to send, where possible. This can make audio quality more resilient to packet loss.
pinless_dialin
array
PAY-AS-YOU-GO
SIP Interconnect and Pinless Dialin,i.e., without entering a PIN code when dialling a phone number or directly calling a Daily SIP Interconnect address. In this case you dont need a SIP address associated to a particular Daily Room.

When a call comes in to this phone number or to the sip interconnect address, it will trigger a webhook, where you'll need to create the Daily room and forward the call to the sipUri assocaited to the newly created room.

The Pinless Dialin only works with purchased phone numbers, because the call is not intended for a particular Daily room. Read more details on our dosc-site.
pin_dialin
array
PAY-AS-YOU-GO
Dialin with a PIN code. This works with both the Global phone numbers and any number that you purchased. When a call comes into one of the phone numbers, the dialer must enter the PIN code. If the code is correct, the user will be connected to the Daily Room. Otherwise the incoming call will be disconnected if an incorrect PIN code is entered.

GET /
This is just about the simplest call you can make with our API, and is a good way to test whether your authorization header is working!


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
      https://api.daily.co/v1/
        

POST /
A POST request to / sets top-level configuration options for your domain.

The request returns a domain object on success. On failure, it returns an HTTP error.

Body params

properties

enable_advanced_chat
boolean
Property that gives end users a richer chat experience. This includes:

Emoji reactions to chat messages
Emoji picker in the chat input form
Ability to send a Giphy chat message
⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_people_ui
boolean
Determines if Daily Prebuilt displays the People UI. When set to true, a People button in the call tray reveals a People tab in the call sidebar. The tab lists all participants, and next to each name indicates audio status and an option to pin the participant. When enable_people_ui is set to false, the button and tab are hidden.

⚠️ Has no effect on custom calls built on the Daily call object.
Default: true
enable_cpu_warning_notifications
boolean
Determines if Daily Prebuilt displays CPU warning notifications. When set to true, snackbar notifications appear when high CPU usage is detected. When set to false, these notifications are hidden.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: true
enable_pip_ui
boolean
Sets whether rooms for this domain can use Daily Prebuilt's Picture in Picture controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle the Picture in Picture feature.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_emoji_reactions
boolean
Determines if Daily Prebuilt displays the Emoji Reactions UI. When set to true, a Reactions button appears in the call tray. This button allows users to select and send a reaction into the call. When set to false, the Reactions button is hidden and the feature is disabled.

Usage: This feature is a good fit for meetings when a host or presenter would benefit from receiving nonverbal cues from the audience. It's also great to keep meetings fun.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_hand_raising
boolean
Sets whether the participants in the room can use Daily Prebuilt's hand raising controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle a hand raise.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_prejoin_ui
boolean
Determines whether participants enter a waiting room with a camera, mic, and browser check before joining a call in any room under this domain.

⚠️ You must be using Daily Prebuilt to use enable_prejoin_ui.
Default: true
enable_breakout_rooms
boolean
Sets whether rooms for this domain have Daily Prebuilt’s breakout rooms feature enabled. When set to true, an owner in a Prebuilt call can create breakout rooms to divide participants into smaller, private groups.

⚠️ You must be using Daily Prebuilt to use enable_breakout_rooms.

⚠️ This property is in beta.
Default: false
enable_live_captions_ui
boolean
Sets whether participants in a room see a closed captions button in their Daily Prebuilt call tray. When the closed caption button is clicked, closed captions are displayed locally.

When set to true, a closed captions button appears in the call tray. When set to false, the closed captions button is hidden from the call tray.

Note: Transcription must be enabled for the room or users must have permission to start transcription for this feature to be enabled. View the transcription guide for more details.

⚠️ You must be using Daily Prebuilt to use enable_live_captions_ui.
Default: false
enable_network_ui
boolean
Determines whether the network button, and the network panel it reveals on click, appears across all rooms belonging to this domain.

⚠️ You must be using Daily Prebuilt to use enable_network_ui.
Default: false
enable_noise_cancellation_ui
boolean
Determines whether Daily Prebuilt displays noise cancellation controls. When set to true, a participant can enable microphone noise cancellation during a Daily Prebuilt call. ⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object. To learn more about adding noise cancellation to a custom application, see the updateInputSettings() docs.
Default: true
enable_video_processing_ui
boolean
Determines whether Daily Prebuilt displays background blur controls. When set to true, a participant can enable blur during a Daily Prebuilt call.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: true
hide_daily_branding
boolean
PAY-AS-YOU-GO
Whether "Powered by Daily" displays in the in-call UI.
Default: false
redirect_on_meeting_exit
string
(For meetings that open in a separate browser tab.) When a user clicks on the in-call menu bar's "leave meeting" button, the browser loads this URL. A query string that includes a parameter of the form recent-call=<domain>/<room> is appended to the URL. On mobile, you can redirect to a deep link to bring a user back into your app.
hipaa
boolean
PAID ADD-ON
Email us at help@daily.co to turn on HIPAA. Learn more about our HIPAA compliance.
Default: false
intercom_auto_record
boolean
Whether to automatically start recording when an Intercom support agent joins an Intercom-created call. Please see our Intercom Messenger App page for more information.

⚠️This method is read-only; please contact us if you'd like to enable intercom call auto-recording.
lang
string
The default language for the video call UI, for all calls.

If you set the language at this domain level, you can still override the setting for specific rooms in a room's configuration properties, or for a specific participant in a meeting token.

You can also set the language dynamically using the front-end library setDailyLang() method.

* Norwegian "no" and Russian "ru" are only available in the new Daily Prebuilt.
Options: "da","de","en","es","fi","fr","it","jp","ka","nl","no","pt","pt-BR","pl","ru","sv","tr","user"
Default: en
meeting_join_hook
string
Sets a URL that will receive a webhook when a user joins a room.

⚠️ In place of the meeting_join_hook, we recommend setting up a webhook and listening for the participant.joined event.
Default: NULL
geo
string
Daily uses signaling servers to manage all of the participants in a given call session. In an SFU/server mode call, the server will send and receive all audio and video from each participant. In a peer-to-peer call, each participant sends media directly to and from each other peer, but a signaling server still manages call state.

Daily runs servers in several different AWS regions to minimize latency for users around the world. The job of 'picking' a call server is handled when the first participant joins a room. The first participant's browser connects to a call server using Amazon's Route 53 DNS resolution, which chooses a server in the region closest to them.

This isn't always optimal. For example, if one person joins in London, and then ten more people join from Cape Town, the call will still be hosted out of eu-west-2 . The majority of the participants will have higher latency to the server than if one of them had joined first and the call was being hosted in af-south-1. In cases like this, you may want to configure your domain (or a specific room) to always choose a call server in a specific AWS region.

Available regions:

"af-south-1" (Cape Town)
"ap-northeast-2" (Seoul)
"ap-southeast-1" (Singapore)
"ap-southeast-2" (Sydney)
"ap-south-1" (Mumbai)
"eu-central-1" (Frankfurt)
"eu-west-2" (London)
"sa-east-1" (São Paulo)
"us-east-1" (N. Virginia)
"us-west-2" (Oregon)
Default: NULL
rtmp_geo
string
Used to select the region where an RTMP stream should originate. In cases where RTMP streaming services aren't available in the desired region, we'll attempt to fall back to the default region based on the SFU being used for the meeting.

Available regions:

"us-west-2" (Oregon)
"eu-central-1" (Frankfurt)
"ap-south-1" (Mumbai)
The default regions are grouped based on the SFU region like so:

RTMP region "us-west-2" includes SFU regions: "us-west-2", "us-east-1", "sa-east-1"
RTMP region "eu-central-1" includes SFU regions: "eu-central-1", "eu-west-2", "af-south-1"
RTMP region "ap-south-1" includes SFU regions: "ap-southeast-1", "ap-southeast-2", "ap-northeast-2", "ap-south-1"
Default: The closest available region to the SFU region used by the meeting.
disable_rtmp_geo_fallback
boolean
Disable the fall back behavior of rtmp_geo. When rtmp_geo is set, we first try to connect to a media server in desired region. If a media server is not available in the desired region, we fall back to default region based on SFU's region. This property disables this automatic fall back. When this property is set, we will trigger a recording/streaming error event when media worker is unavailable. Also, the client should retry recording/streaming.
Default: false
enable_terse_logging
boolean
Reduces the volume of log messages. This feature should be enabled when there are more than 200 participants in a meeting to help improve performance.

See our guides for supporting large experiences for additional instruction.
Default: false
enable_transcription_storage
boolean
Live transcriptions generated can be saved as WebVTT. This flag controls if transcription started with startTranscription() should be saved or not.
Default: false
transcription_bucket
object
Configures an S3 bucket in which to store transcriptions. See the S3 bucket guide for more information.
bucket_name
string
The name of the Amazon S3 bucket to use for transcription storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the transcription in the specified bucket.
allow_api_access
boolean
Whether the transcription should be accessible using Daily's API.
recordings_template
string
Cloud recordings are stored in either Daily's S3 bucket or the customer's own S3 bucket. By default recordings are stored as {domain_name}/{room_name}/{epoch_time}. Sometimes, the use case may call for custom recording file names to be used (for example, if you'd like to enforce the presence of the .mp4 extension in the file name).

recordings_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in milliseconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting recorded (optional)
mtg_session_id: The ID of the meeting session which is getting recorded (optional)
instance_id: The instance ID of the recording (optional)
recording_id: The recording ID of the recording (optional)
The restrictions for defining a recording template are as follows:

The epoch_time tag is mandatory to ensure the recording file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
.mp4 is the only valid extension
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.
transcription_template
string
transcriptions can be stored in either Daily's S3 bucket or the customer's own S3 bucket. By default transcriptions are stored as {domain_name}/{room_name}/{epoch_time}.vtt. Sometimes, the use case may call for custom file path to be used (for example, if you'd like to map stored transcription to mtgSessionId).

transcription_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in seconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting transcribed (optional)
mtg_session_id: The ID of the meeting session which is getting transcribed (optional)
instance_id: The instance ID of the transcription (optional)
transcript_id: The transcript ID of the transcription (optional)
The restrictions for defining a transcription template are as follows:

The epoch_time tag is mandatory to ensure the transcription file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.vtt.
enable_mesh_sfu
boolean
Configures a room to use multiple SFUs for a call's media. This feature enables calls to scale to large sizes and to reduce latency between participants. It is recommended specifically for interactive live streaming.

See our guide for interactive live streaming for additional instruction.
sfu_switchover
number
Dictates the participant count after which room topology automatically switches from Peer-to-Peer (P2P) to Selective Forwarding Unit (SFU) mode, or vice versa.

For example, if sfu_switchover is set to 2 and the current network topology is P2P, the topology will switch to SFU mode when the third participant joins the call. If the current topology is SFU, it will switch to P2P mode when the participant count decreases from 2 to 1.

We recommend specifying an integer value for this property except for cases where you would like the room to switch to SFU mode as soon as the first participant joins. In this case, set sfu_switchover to 0.5.

See our guide about video call architecture for additional information.
Default: 0.5
enable_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_adaptive_simulcast to true will enable Daily Adaptive Bitrate for 1:1 calls.
Default: true
enforce_unique_user_ids
boolean
Configures a domain or room to disallow multiple participants from having the same user_id. This feature can be enabled to prevent users from "sharing" meeting tokens. When enabled, a participant joining or reconnecting to a meeting will cause existing participants with the same user_id to be ejected.
Default: false
recordings_bucket
object
Configures an S3 bucket in which to store recordings. See the S3 bucket guide for more information.

Properties:
bucket_name
string
The name of the Amazon S3 bucket to use for recording storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the recording in the specified bucket.
allow_api_access
boolean
Controls whether the recording will be accessible using Daily's API.
allow_streaming_from_bucket
boolean
Specifies which Content-Disposition response header the recording link retrieved from the access-link REST API endpoint will have. If allow_streaming_from_bucket is false, the header will be Content-Dispostion: attachment. If allow_streaming_from_bucket is true, the header will be Content-Disposition: inline. To play the recording link directly in the browser or embed it in a video player, set this property to true.
Default: false
permissions
object
Specifies the initial default permissions for a non-meeting-owner participant joining a call.

Each permission (i.e. each of the properties listed below) can be configured in the meeting token, the room, and/or the domain, in decreasing order of precedence.

Participant admins (those with the 'participants' value in their canAdmin permission) can also change participants' permissions on the fly during a call using updateParticipant() or updateParticipants().
hasPresence
boolean
Whether the participant appears as "present" in the call, i.e. whether they appear in participants().
canSend
boolean | array
Which types of media a participant should be permitted to send.

Can be:

An Array containing any of 'video', 'audio', 'screenVideo', and 'screenAudio'
true (meaning "all")
false (meaning "none")
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
boolean | array
Which admin tasks a participant is permitted to do.

Can be:

An array containing any of 'participants', 'streaming', or 'transcription'
true (meaning "all")
false (meaning "none")
Default: { canSend: true, canReceive: { base: true }, hasPresence: true, canAdmin: false }
batch_processor_bucket
object
Defines a custom S3 bucket where the batch processor will write its output
enable_opus_fec
boolean
Enables the use of Opus in-band FEC (Forward Error Correction) when encoding audio to send, where possible. This can make audio quality more resilient to packet loss.
pinless_dialin
array
PAY-AS-YOU-GO
SIP Interconnect and Pinless Dialin,i.e., without entering a PIN code when dialling a phone number or directly calling a Daily SIP Interconnect address. In this case you dont need a SIP address associated to a particular Daily Room.

When a call comes in to this phone number or to the sip interconnect address, it will trigger a webhook, where you'll need to create the Daily room and forward the call to the sipUri assocaited to the newly created room.

The Pinless Dialin only works with purchased phone numbers, because the call is not intended for a particular Daily room. Read more details on our dosc-site.
pin_dialin
array
PAY-AS-YOU-GO
Dialin with a PIN code. This works with both the Global phone numbers and any number that you purchased. When a call comes into one of the phone numbers, the dialer must enter the PIN code. If the code is correct, the user will be connected to the Daily Room. Otherwise the incoming call will be disconnected if an incorrect PIN code is entered.
Example requests

Set a domain property


Request

200 OK
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -XPOST -d '{"properties":{"redirect_on_meeting_exit": "https://my-site.com/"}}' \
    https://api.daily.co/v1/
        
Unset a domain property

To unset any domain configuration property — in other words, to reset any property to its default value — set the property to null. For example:

cURL
Copy to clipboard
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer DAILY_API_KEY" \
     -XPOST -d '{"properties": {"redirect_on_meeting_exit": null}}' \
     https://api.daily.co/v1/

The "room" object
A "room" represents a specific video call location and configuration. You can list, create, configure, and delete rooms with the Daily API.

JSON
Copy to clipboard
{
  "id": "5e3cf703-5547-47d6-a371-37b1f0b4427f",
  "name": "hello",
  "api_created": false,
  "privacy": "public",
  "url": "https://api-demo.daily.co/hello",
  "created_at": "2019-01-25T23:49:42.000Z",
  "config": {
    "max_participants": 4,
    "nbf": 1548547221,
    "exp": 1548633621
    "start_video_off": true,
    "enable_recording": 'cloud',
  }
}

A room contains a url property. A participant joins a Daily video call via a room URL.

A room URL looks like this: https://<your-domain>.daily.co/<room-name>/.

A participant joins a Daily video call by opening the room URL directly in a browser tab (recommended for testing only), or by accessing the link from an embedded iframe (Daily’s prebuilt UI) or within a custom app built on the Daily call object.

Heads up!
Hard-coding Daily room URLs is fine for testing locally, but a security liability in production. You'll want to generate room URLs server side.
Tutorial: Deploying a Daily backend server instantly with Glitch and Node.js.
Rooms can be created either manually in the Daily dashboard or by a POST to the /rooms API endpoint.

You can specify configuration properties when you create the room. All rooms come with a few default settings, unless you configure them otherwise.

By default, the privacy property is set to "public". Anyone who knows the room's name can join the room, and anybody with access to the URL can enter. This is often what you want. It's easy to create rooms that have unique, unguessable, names. But, you can also change a room's privacy setting and control who can join a room.

More resources on room privacy
Intro to room access control
Add advanced security to video chats with the Daily API.
By default, rooms are permanent and always available. To limit that access, you can set two fields to control when participants can join a meeting in a room. nbf stands for "not before". If the nbf configuration field is set, participants can’t connect to the room before that time. exp is short for "expires." If the exp configuration flag is set, participants are not able to connect to the room after that time.

Note that nbf and exp only control whether users are allowed to join a meeting in a room. Users who are in a meeting when a room expires are not kicked out of the meeting, unless you set the eject_at_room_exp property.

Rooms that have an exp in the past are not returned by the list rooms endpoint; they are zombies of a sort. An existing meeting can continue in the room, but from the perspective of most of the API, the room does not exist!

If you ever need to kick everyone out of a room unexpectedly, you can delete the room. (You can always recreate a room with the same name, later.)

Configuration
You can configure Daily rooms with three different parameters: name, privacy, and a properties object.

name

name
string
Defaults to a randomly generated string A room name can include only the uppercase and lowercase ascii letters, numbers, dash and underscore. In other words, this regexp detects an invalid room name: /[^A-Za-z0-9_-]/.

The room name cannot exceed 128 characters. You'll get an error if you try to create a room with a name that's too long.

If you supply a name for the room, the room will (if possible) be created with that name. Otherwise a random room name — something like 'w2pp2cf4kltgFACPKXmX' — will be generated.

Human-readable room names are great for lots of applications! The room's name is part of the room's URL, and anyone you send the URL to, or who opens the URL in a new browser tab, will see the name.

If you don't care about having a human-readable room name, just don't supply a name parameter.
privacy

privacy
string
Determines who can access the room.
Options: "public","private"
Default: "public"
More resources on room privacy
An introduction to room access control
Add advanced security to video chats with the Daily API
Controlling who joins a meeting
properties

Most properties determine what features appear when using the Daily prebuilt UI.

nbf
integer
"Not before". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in this room before this time.
exp
integer
"Expires". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in this room after this time.

More resources:

Add advanced security to video chats with the Daily API
max_participants
integer
PAY-AS-YOU-GO
How many people are allowed in a room at the same time.

⚠️ Contact us if you need to set the limit above 200.
Default: 200
enable_people_ui
boolean
Determines if Daily Prebuilt displays the People UI. When set to true, a People button in the call tray reveals a People tab in the call sidebar. The tab lists all participants, and next to each name indicates audio status and an option to pin the participant. When enable_people_ui is set to false, the button and tab are hidden.

⚠️ Has no effect on custom calls built on the Daily call object.
enable_cpu_warning_notifications
boolean
Determines if Daily Prebuilt displays CPU warning notifications. When set to true, snackbar notifications appear when high CPU usage is detected. When set to false, these notifications are hidden.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_pip_ui
boolean
Sets whether the room can use Daily Prebuilt's Picture in Picture controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle the Picture in Picture feature.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_emoji_reactions
boolean
Determines if Daily Prebuilt displays the Emoji Reactions UI. When set to true, a Reactions button appears in the call tray. This button allows users to select and send a reaction into the call. When set to false, the Reactions button is hidden and the feature is disabled.

Usage: This feature is a good fit for meetings when a host or presenter would benefit from receiving nonverbal cues from the audience. It's also great to keep meetings fun.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_hand_raising
boolean
Sets whether the participants in the room can use Daily Prebuilt's hand raising controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle a hand raise.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_prejoin_ui
boolean
Determines whether participants enter a waiting room with a camera, mic, and browser check before joining a call.

⚠️ You must be using Daily Prebuilt to use enable_prejoin_ui.
enable_live_captions_ui
boolean
Sets whether participants in a room see a closed captions button in their Daily Prebuilt call tray. When the closed caption button is clicked, closed captions are displayed locally.

When set to true, a closed captions button appears in the call tray. When set to false, the closed captions button is hidden from the call tray.

Note: Transcription must be enabled for the room or users must have permission to start transcription for this feature to be enabled. View the transcription guide for more details.

⚠️ You must be using Daily Prebuilt to use enable_live_captions_ui.
enable_network_ui
boolean
Determines whether the network button, and the network panel it reveals on click, appears in this room.

⚠️ You must be using Daily Prebuilt to use enable_network_ui.
enable_noise_cancellation_ui
boolean
Determines whether Daily Prebuilt displays noise cancellation controls. When set to true, a participant can enable microphone noise cancellation during a Daily Prebuilt call. ⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object. To learn more about adding noise cancellation to a custom application, see the updateInputSettings() docs.
enable_breakout_rooms
boolean
Sets whether Daily Prebuilt’s breakout rooms feature is enabled. When set to true, an owner in a Prebuilt call can create breakout rooms to divide participants into smaller, private groups.

⚠️ You must be using Daily Prebuilt to use enable_breakout_rooms.

⚠️ This property is in beta.
enable_knocking
boolean
Turns on a lobby experience for private rooms. A participant without a corresponding meeting token can request to be admitted to the meeting with a "knock", and wait for the meeting owner to admit them.
enable_screenshare
boolean
Sets whether users in a room can screen share during a session. This property cannot be changed after a session starts. For dynamic control over permissions, use the updateParticipant() method to control user permissions.
Default: true
enable_video_processing_ui
boolean
Determines whether Daily Prebuilt displays background blur controls. When set to true, a participant can enable blur during a Daily Prebuilt call.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: true
enable_chat
boolean
This property is one of multiple ways to add chat to Daily video calls.
Default: false
enable_shared_chat_history
boolean
When enabled, newly joined participants in Prebuilt calls will request chat history from remote peers, in order to view chat messages from before they joined.
Default: true
start_video_off
boolean
Disable the default behavior of automatically turning on a participant's camera on a direct join() (i.e. without startCamera() first).
Default: false
start_audio_off
boolean
Disable the default behavior of automatically turning on a participant's microphone on a direct join() (i.e. without startCamera() first).
Default: false
owner_only_broadcast
boolean
In Daily Prebuilt, only the meeting owners will be able to turn on camera, unmute mic, and share screen.

See setting up calls.
Default: false
enable_recording
string
Jump to recording docs.
Options: "cloud","local","raw-tracks","<not set>"
Default: <not set>
eject_at_room_exp
boolean
If there's a meeting going on at room exp time, end the meeting by kicking everyone out. This behavior can be overridden by setting eject properties of a meeting token.
Default: false
eject_after_elapsed
integer
Eject a meeting participant this many seconds after the participant joins the meeting. You can use this is a default length limit to prevent long meetings. This can be overridden by setting eject properties of a meeting token.
enable_advanced_chat
boolean
Property that gives end users a richer chat experience. This includes:

Emoji reactions to chat messages
Emoji picker in the chat input form
Ability to send a Giphy chat message
⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_hidden_participants
boolean
When enabled, non-owner users join a meeting with a hidden presence, meaning they won't appear as a named participant in the meeting and have no participant events associated to them. Additionally, these participants can only receive media tracks from owner participants.

Hidden participants can be tracked using the participantCounts() method. Hidden participants do not have entries in the participants() method return value.

When used with Daily Prebuilt, hidden participants are included in the participant count available in the UI; however, are not included in the People panel and can only read chat messages.

This property should be used to support hosting large meetings. See our guide on interactive live streaming for additional instruction.
Default: false
enable_mesh_sfu
boolean
Configures a room to use multiple SFUs for a call's media. This feature enables calls to scale to large sizes and to reduce latency between participants. It is recommended specifically for interactive live streaming.

See our guide for interactive live streaming for additional instruction.
sfu_switchover
number
Dictates the participant count after which room topology automatically switches from Peer-to-Peer (P2P) to Selective Forwarding Unit (SFU) mode, or vice versa.

For example, if sfu_switchover is set to 2 and the current network topology is P2P, the topology will switch to SFU mode when the third participant joins the call. If the current topology is SFU, it will switch to P2P mode when the participant count decreases from 2 to 1.

We recommend specifying an integer value for this property except for cases where you would like the room to switch to SFU mode as soon as the first participant joins. In this case, set sfu_switchover to 0.5.

See our guide about video call architecture for additional information.
Default: 0.5
enable_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_adaptive_simulcast to true will enable Daily Adaptive Bitrate for 1:1 calls.
Default: true
enable_multiparty_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_multiparty_adaptive_simulcast to true will enable Daily Adaptive Bitrate for multi-party calls. To use this feature, enable_adaptive_simulcast must also be set to true.
Default: false
enforce_unique_user_ids
boolean
Configures a domain or room to disallow multiple participants from having the same user_id. This feature can be enabled to prevent users from "sharing" meeting tokens. When enabled, a participant joining or reconnecting to a meeting will cause existing participants with the same user_id to be ejected.
Default: false
experimental_optimize_large_calls
boolean
Enables Daily Prebuilt to support group calls of up to 1,000 participants and owner only broadcast calls of up to 100K participants.

When set to true, Daily Prebuilt will:

Automatically mute the local user on joining
Update grid view to show a maximum of 12 users in the grid at a time
Allow only 16 users to be unmuted at the same time. When more than 16 users are unmuted, the oldest active speaker will be automatically muted.
See our guide on large real-time calls for additional instruction.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
lang
string
The default language of the Daily prebuilt video call UI, for this room.

Setting the language at the room level will override any domain-level language settings you have.

Read more about changing prebuilt UI language settings.

* Norwegian "no" and Russian "ru" are only available in the new Daily Prebuilt.
Options: "da","de","en","es","fi","fr","it","jp","ka","nl","no","pt","pt-BR","pl","ru","sv","tr","user"
Default: en
meeting_join_hook
string
Sets a URL that will receive a webhook when a user joins a room. Default is NULL. Character limit for webhook URL is 255.

⚠️ In place of the meeting_join_hook, we recommend setting up a webhook and listening for the participant.joined event.
geo
string
Daily uses signaling servers to manage all of the participants in a given call session. In an SFU/server mode call, the server will send and receive all audio and video from each participant. In a peer-to-peer call, each participant sends media directly to and from each other peer, but a signaling server still manages call state.

Daily runs servers in several different AWS regions to minimize latency for users around the world. The job of 'picking' a call server is handled when the first participant joins a room. The first participant's browser connects to a call server using Amazon's Route 53 DNS resolution, which chooses a server in the region closest to them.

This isn't always optimal. For example, if one person joins in London, and then ten more people join from Cape Town, the call will still be hosted out of eu-west-2 . The majority of the participants will have higher latency to the server than if one of them had joined first and the call was being hosted in af-south-1. In cases like this, you may want to configure your domain (or a specific room) to always choose a call server in a specific AWS region.

Available regions:

"af-south-1" (Cape Town)
"ap-northeast-2" (Seoul)
"ap-southeast-1" (Singapore)
"ap-southeast-2" (Sydney)
"ap-south-1" (Mumbai)
"eu-central-1" (Frankfurt)
"eu-west-2" (London)
"sa-east-1" (São Paulo)
"us-east-1" (N. Virginia)
"us-west-2" (Oregon)
Default: NULL
rtmp_geo
string
Used to select the region where an RTMP stream should originate. In cases where RTMP streaming services aren't available in the desired region, we'll attempt to fall back to the default region based on the SFU being used for the meeting.

Available regions:

"us-west-2" (Oregon)
"eu-central-1" (Frankfurt)
"ap-south-1" (Mumbai)
The default regions are grouped based on the SFU region like so:

RTMP region "us-west-2" includes SFU regions: "us-west-2", "us-east-1", "sa-east-1"
RTMP region "eu-central-1" includes SFU regions: "eu-central-1", "eu-west-2", "af-south-1"
RTMP region "ap-south-1" includes SFU regions: "ap-southeast-1", "ap-southeast-2", "ap-northeast-2", "ap-south-1"
Default: The closest available region to the SFU region used by the meeting.
disable_rtmp_geo_fallback
boolean
Disable the fall back behavior of rtmp_geo. When rtmp_geo is set, we first try to connect to a media server in desired region. If a media server is not available in the desired region, we fall back to default region based on SFU's region. This property disables this automatic fall back. When this property is set, we will trigger a recording/streaming error event when media worker is unavailable. Also, the client should retry recording/streaming.
Default: false
recordings_bucket
object
Configures an S3 bucket in which to store recordings. See the S3 bucket guide for more information.

Properties:
bucket_name
string
The name of the Amazon S3 bucket to use for recording storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the recording in the specified bucket.
allow_api_access
boolean
Controls whether the recording will be accessible using Daily's API.
allow_streaming_from_bucket
boolean
Specifies which Content-Disposition response header the recording link retrieved from the access-link REST API endpoint will have. If allow_streaming_from_bucket is false, the header will be Content-Dispostion: attachment. If allow_streaming_from_bucket is true, the header will be Content-Disposition: inline. To play the recording link directly in the browser or embed it in a video player, set this property to true.
Default: false
enable_terse_logging
boolean
Reduces the volume of log messages. This feature should be enabled when there are more than 200 participants in a meeting to help improve performance.

See our guides for supporting large experiences for additional instruction.
Default: false
auto_transcription_settings
object
PAY-AS-YOU-GO
Options to use when auto_start_transcription is true. See startTranscription() for available options.
enable_transcription_storage
boolean
Live transcriptions generated can be saved as WebVTT. This flag controls if transcription started with startTranscription() should be saved or not.
Default: false
transcription_bucket
object
Configures an S3 bucket in which to store transcriptions. See the S3 bucket guide for more information.
bucket_name
string
The name of the Amazon S3 bucket to use for transcription storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the transcription in the specified bucket.
allow_api_access
boolean
Whether the transcription should be accessible using Daily's API.
recordings_template
string
Cloud recordings are stored in either Daily's S3 bucket or the customer's own S3 bucket. By default recordings are stored as {domain_name}/{room_name}/{epoch_time}. Sometimes, the use case may call for custom recording file names to be used (for example, if you'd like to enforce the presence of the .mp4 extension in the file name).

recordings_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in milliseconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting recorded (optional)
mtg_session_id: The ID of the meeting session which is getting recorded (optional)
instance_id: The instance ID of the recording (optional)
recording_id: The recording ID of the recording (optional)
The restrictions for defining a recording template are as follows:

The epoch_time tag is mandatory to ensure the recording file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
.mp4 is the only valid extension
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.
transcription_template
string
transcriptions can be stored in either Daily's S3 bucket or the customer's own S3 bucket. By default transcriptions are stored as {domain_name}/{room_name}/{epoch_time}.vtt. Sometimes, the use case may call for custom file path to be used (for example, if you'd like to map stored transcription to mtgSessionId).

transcription_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in seconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting transcribed (optional)
mtg_session_id: The ID of the meeting session which is getting transcribed (optional)
instance_id: The instance ID of the transcription (optional)
transcript_id: The transcript ID of the transcription (optional)
The restrictions for defining a transcription template are as follows:

The epoch_time tag is mandatory to ensure the transcription file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.vtt.
enable_dialout
boolean
Allow dialout API from the room.
Default: false
dialout_config
object
Allow configuring dialout behaviour.
allow_room_start
boolean
Setting this to true allows starting the room and initiating the dial-out even though there is no user present in the room. By default, initiating a dial-out via the REST API fails when the corresponding room is empty (without any participant).
Default: false
dialout_geo
string
The region where SFU is selected to start the room. default is taken from room geo else from domain geo and if both are not defined us-west-2 is take as default.
max_idle_timeout_sec
number
Number of seconds where dialout user can be alone in the room. dialout user can start the room and can remain in the room alone waiting for other participant for this duration, also when all the web users leave the room, room is automatically closed, this property allows dialout user to remain in room after all web users leave the room.
Default: 0
streaming_endpoints
array
An array of stream endpoint configuration objects, which allows configurations to be pre-defined without having to pass them into startLiveStreaming() at runtime. For example, an RTMP endpoint can be set up for YouTube as a streaming_endpoints configuration along with another configuration for HLS storage.

HLS output can only be stored on a customer's S3, not in Daily's storage infrastructure. The stream configuration defines which S3 bucket to store the HLS output. (See the S3 bucket guide for more information.)

Example:

JSON
Copy to clipboard

{
  "properties": {
    // ... add additional room properties here
    "streaming_endpoints": [
      {
        "name": "rtmp_youtube",
        "type": "rtmp",
        "rtmp_config": {
          "url": "rtmps://exampleYouTubeServer.com:443/stream"
        }
      },

      {
        "name": "rtmp_ivs",
        "type": "rtmp",
        "rtmp_config": {
          "url": "rtmps://811111111111.global-contribute.live-video.net:443/app/"
        }
      },

      {
        "name": "hls_akamai",
        "type": "hls",
        "hls_config": {
        "save_hls_recording": true/false,
          "storage": {
            "bucket_name": "daily-hls-streams",
            "bucket_region": "us-west-2",
            "assume_role_arn": "arn:aws:iam::999999999999:role/DailyS3AccessRole",
            "path_template": "testHarness/{live_streaming_id}/{instance_id}"
          },
          "variant" : [
              {
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "bitrate": 3500,
                "iframe_only": false
              },
              {
                "width": 1280,
                "height": 720,
                "fps": 30,
                "bitrate": 2500,
                "iframe_only": false
              },
              {
                "width": 640,
                "height": 360,
                "fps": 30,
                "bitrate": 780,
                "iframe_only": true
              }
          ]
        }
      }
    ]
  }
}

To reset the streaming_endpoints property, pass null instead of an array.

When calling startLiveStreaming(), the pre-defined streaming_endpoints name can be used:

JavaScript
Copy to clipboard
await callObject.startLiveStreaming({
  endpoints: [{"endpoint":"rtmp_youtube"},{"endpoint":"rtmp_fb"}],
  width: 1280,
  height: 720,
});

Properties:
permissions
object
Specifies the initial default permissions for a non-meeting-owner participant joining a call.

Each permission (i.e. each of the properties listed below) can be configured in the meeting token, the room, and/or the domain, in decreasing order of precedence.

Participant admins (those with the 'participants' value in their canAdmin permission) can also change participants' permissions on the fly during a call using updateParticipant() or updateParticipants().
hasPresence
boolean
Whether the participant appears as "present" in the call, i.e. whether they appear in participants().
canSend
boolean | array
Which types of media a participant should be permitted to send.

Can be:

An Array containing any of 'video', 'audio', 'screenVideo', and 'screenAudio'
true (meaning "all")
false (meaning "none")
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
boolean | array
Which admin tasks a participant is permitted to do.

Can be:

An array containing any of 'participants', 'streaming', or 'transcription'
true (meaning "all")
false (meaning "none")
Default: <not set>

GET /rooms
A GET request to /rooms returns a list of rooms in your domain.

Rooms are returned sorted by created_at_time in reverse chronological order (your most recent room comes first; oldest latest).

Each call to this endpoint fetches a maximum of 100 room objects.

The response body consists of two fields: total_count and data.

The total_count field is the total number of rooms in the domain. The count includes rooms outside the scope of the request, e.g. if you’ve created +100 rooms, exceeding the request limit, or if you’ve provided started_before or ending_before arguments.

The data field is a list of room objects.

Query params

limit
int32
Sets the number of rooms listed
ending_before
string
Returns room objects created before a provided room id
starting_after
string
Returns room objects created after a provided room id
Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     https://api.daily.co/v1/rooms?limit=5
        
When a room object is returned by an API call, only configuration options that differ from the defaults are included in the config struct.

Further reading
Room configuration
How to use the limit, ending_before, and starting_after query parameters

POST /rooms
A POST request to /rooms creates a new room.

If the room is created, a room object is returned. So you can, for example, create a room, then immediately grab the room url from the API response and use it in your user interface. If you don't set privacy configuration parameters when you create the room, you can always set/change them later.

The config part of the room object includes only configuration parameters that differ from room configuration defaults.

If the room is not created, you'll get back an HTTP error, with information about the error in the HTTP response body.

Body params

A POST request has three optional body parameters: name, privacy, and a properties object.

name

name
string
Defaults to a randomly generated string. A room name can include only the uppercase and lowercase ascii letters, numbers, dash and underscore. In other words, this regexp detects an invalid room name: /[^A-Za-z0-9_-]/.

The room name cannot exceed 128 characters. You'll get an error if you try to create a room with a name that's too long.
privacy

privacy
string
Determines who can access the room.
Options: "public","private"
Default: "public"
properties

nbf
integer
"Not before". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in this room before this time.
exp
integer
"Expires". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in this room after this time.

More resources:

Add advanced security to video chats with the Daily API
max_participants
integer
PAY-AS-YOU-GO
How many people are allowed in a room at the same time.

⚠️ Contact us if you need to set the limit above 200.
Default: 200
enable_people_ui
boolean
Determines if Daily Prebuilt displays the People UI. When set to true, a People button in the call tray reveals a People tab in the call sidebar. The tab lists all participants, and next to each name indicates audio status and an option to pin the participant. When enable_people_ui is set to false, the button and tab are hidden.

⚠️ Has no effect on custom calls built on the Daily call object.
enable_cpu_warning_notifications
boolean
Determines if Daily Prebuilt displays CPU warning notifications. When set to true, snackbar notifications appear when high CPU usage is detected. When set to false, these notifications are hidden.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_pip_ui
boolean
Sets whether the room can use Daily Prebuilt's Picture in Picture controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle the Picture in Picture feature.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_emoji_reactions
boolean
Determines if Daily Prebuilt displays the Emoji Reactions UI. When set to true, a Reactions button appears in the call tray. This button allows users to select and send a reaction into the call. When set to false, the Reactions button is hidden and the feature is disabled.

Usage: This feature is a good fit for meetings when a host or presenter would benefit from receiving nonverbal cues from the audience. It's also great to keep meetings fun.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_hand_raising
boolean
Sets whether the participants in the room can use Daily Prebuilt's hand raising controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle a hand raise.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_prejoin_ui
boolean
Determines whether participants enter a waiting room with a camera, mic, and browser check before joining a call.

⚠️ You must be using Daily Prebuilt to use enable_prejoin_ui.
enable_live_captions_ui
boolean
Sets whether participants in a room see a closed captions button in their Daily Prebuilt call tray. When the closed caption button is clicked, closed captions are displayed locally.

When set to true, a closed captions button appears in the call tray. When set to false, the closed captions button is hidden from the call tray.

Note: Transcription must be enabled for the room or users must have permission to start transcription for this feature to be enabled. View the transcription guide for more details.

⚠️ You must be using Daily Prebuilt to use enable_live_captions_ui.
enable_network_ui
boolean
Determines whether the network button, and the network panel it reveals on click, appears in this room.

⚠️ You must be using Daily Prebuilt to use enable_network_ui.
enable_noise_cancellation_ui
boolean
Determines whether Daily Prebuilt displays noise cancellation controls. When set to true, a participant can enable microphone noise cancellation during a Daily Prebuilt call. ⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object. To learn more about adding noise cancellation to a custom application, see the updateInputSettings() docs.
enable_breakout_rooms
boolean
Sets whether Daily Prebuilt’s breakout rooms feature is enabled. When set to true, an owner in a Prebuilt call can create breakout rooms to divide participants into smaller, private groups.

⚠️ You must be using Daily Prebuilt to use enable_breakout_rooms.

⚠️ This property is in beta.
enable_knocking
boolean
Turns on a lobby experience for private rooms. A participant without a corresponding meeting token can request to be admitted to the meeting with a "knock", and wait for the meeting owner to admit them.
enable_screenshare
boolean
Sets whether users in a room can screen share during a session. This property cannot be changed after a session starts. For dynamic control over permissions, use the updateParticipant() method to control user permissions.
Default: true
enable_video_processing_ui
boolean
Determines whether Daily Prebuilt displays background blur controls. When set to true, a participant can enable blur during a Daily Prebuilt call.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: true
enable_chat
boolean
This property is one of multiple ways to add chat to Daily video calls.
Default: false
enable_shared_chat_history
boolean
When enabled, newly joined participants in Prebuilt calls will request chat history from remote peers, in order to view chat messages from before they joined.
Default: true
start_video_off
boolean
Disable the default behavior of automatically turning on a participant's camera on a direct join() (i.e. without startCamera() first).
Default: false
start_audio_off
boolean
Disable the default behavior of automatically turning on a participant's microphone on a direct join() (i.e. without startCamera() first).
Default: false
owner_only_broadcast
boolean
In Daily Prebuilt, only the meeting owners will be able to turn on camera, unmute mic, and share screen.

See setting up calls.
Default: false
enable_recording
string
Jump to recording docs.
Options: "cloud","local","raw-tracks","<not set>"
Default: <not set>
eject_at_room_exp
boolean
If there's a meeting going on at room exp time, end the meeting by kicking everyone out. This behavior can be overridden by setting eject properties of a meeting token.
Default: false
eject_after_elapsed
integer
Eject a meeting participant this many seconds after the participant joins the meeting. You can use this is a default length limit to prevent long meetings. This can be overridden by setting eject properties of a meeting token.
enable_advanced_chat
boolean
Property that gives end users a richer chat experience. This includes:

Emoji reactions to chat messages
Emoji picker in the chat input form
Ability to send a Giphy chat message
⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_hidden_participants
boolean
When enabled, non-owner users join a meeting with a hidden presence, meaning they won't appear as a named participant in the meeting and have no participant events associated to them. Additionally, these participants can only receive media tracks from owner participants.

Hidden participants can be tracked using the participantCounts() method. Hidden participants do not have entries in the participants() method return value.

When used with Daily Prebuilt, hidden participants are included in the participant count available in the UI; however, are not included in the People panel and can only read chat messages.

This property should be used to support hosting large meetings. See our guide on interactive live streaming for additional instruction.
Default: false
enable_mesh_sfu
boolean
Configures a room to use multiple SFUs for a call's media. This feature enables calls to scale to large sizes and to reduce latency between participants. It is recommended specifically for interactive live streaming.

See our guide for interactive live streaming for additional instruction.
sfu_switchover
number
Dictates the participant count after which room topology automatically switches from Peer-to-Peer (P2P) to Selective Forwarding Unit (SFU) mode, or vice versa.

For example, if sfu_switchover is set to 2 and the current network topology is P2P, the topology will switch to SFU mode when the third participant joins the call. If the current topology is SFU, it will switch to P2P mode when the participant count decreases from 2 to 1.

We recommend specifying an integer value for this property except for cases where you would like the room to switch to SFU mode as soon as the first participant joins. In this case, set sfu_switchover to 0.5.

See our guide about video call architecture for additional information.
Default: 0.5
enable_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_adaptive_simulcast to true will enable Daily Adaptive Bitrate for 1:1 calls.
Default: true
enable_multiparty_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_multiparty_adaptive_simulcast to true will enable Daily Adaptive Bitrate for multi-party calls. To use this feature, enable_adaptive_simulcast must also be set to true.
Default: false
enforce_unique_user_ids
boolean
Configures a domain or room to disallow multiple participants from having the same user_id. This feature can be enabled to prevent users from "sharing" meeting tokens. When enabled, a participant joining or reconnecting to a meeting will cause existing participants with the same user_id to be ejected.
Default: false
experimental_optimize_large_calls
boolean
Enables Daily Prebuilt to support group calls of up to 1,000 participants and owner only broadcast calls of up to 100K participants.

When set to true, Daily Prebuilt will:

Automatically mute the local user on joining
Update grid view to show a maximum of 12 users in the grid at a time
Allow only 16 users to be unmuted at the same time. When more than 16 users are unmuted, the oldest active speaker will be automatically muted.
See our guide on large real-time calls for additional instruction.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
lang
string
The default language of the Daily prebuilt video call UI, for this room.

Setting the language at the room level will override any domain-level language settings you have.

Read more about changing prebuilt UI language settings.

* Norwegian "no" and Russian "ru" are only available in the new Daily Prebuilt.
Options: "da","de","en","es","fi","fr","it","jp","ka","nl","no","pt","pt-BR","pl","ru","sv","tr","user"
Default: en
meeting_join_hook
string
Sets a URL that will receive a webhook when a user joins a room. Default is NULL. Character limit for webhook URL is 255.

⚠️ In place of the meeting_join_hook, we recommend setting up a webhook and listening for the participant.joined event.
geo
string
Daily uses signaling servers to manage all of the participants in a given call session. In an SFU/server mode call, the server will send and receive all audio and video from each participant. In a peer-to-peer call, each participant sends media directly to and from each other peer, but a signaling server still manages call state.

Daily runs servers in several different AWS regions to minimize latency for users around the world. The job of 'picking' a call server is handled when the first participant joins a room. The first participant's browser connects to a call server using Amazon's Route 53 DNS resolution, which chooses a server in the region closest to them.

This isn't always optimal. For example, if one person joins in London, and then ten more people join from Cape Town, the call will still be hosted out of eu-west-2 . The majority of the participants will have higher latency to the server than if one of them had joined first and the call was being hosted in af-south-1. In cases like this, you may want to configure your domain (or a specific room) to always choose a call server in a specific AWS region.

Available regions:

"af-south-1" (Cape Town)
"ap-northeast-2" (Seoul)
"ap-southeast-1" (Singapore)
"ap-southeast-2" (Sydney)
"ap-south-1" (Mumbai)
"eu-central-1" (Frankfurt)
"eu-west-2" (London)
"sa-east-1" (São Paulo)
"us-east-1" (N. Virginia)
"us-west-2" (Oregon)
Default: NULL
rtmp_geo
string
Used to select the region where an RTMP stream should originate. In cases where RTMP streaming services aren't available in the desired region, we'll attempt to fall back to the default region based on the SFU being used for the meeting.

Available regions:

"us-west-2" (Oregon)
"eu-central-1" (Frankfurt)
"ap-south-1" (Mumbai)
The default regions are grouped based on the SFU region like so:

RTMP region "us-west-2" includes SFU regions: "us-west-2", "us-east-1", "sa-east-1"
RTMP region "eu-central-1" includes SFU regions: "eu-central-1", "eu-west-2", "af-south-1"
RTMP region "ap-south-1" includes SFU regions: "ap-southeast-1", "ap-southeast-2", "ap-northeast-2", "ap-south-1"
Default: The closest available region to the SFU region used by the meeting.
disable_rtmp_geo_fallback
boolean
Disable the fall back behavior of rtmp_geo. When rtmp_geo is set, we first try to connect to a media server in desired region. If a media server is not available in the desired region, we fall back to default region based on SFU's region. This property disables this automatic fall back. When this property is set, we will trigger a recording/streaming error event when media worker is unavailable. Also, the client should retry recording/streaming.
Default: false
recordings_bucket
object
Configures an S3 bucket in which to store recordings. See the S3 bucket guide for more information.

Properties:
bucket_name
string
The name of the Amazon S3 bucket to use for recording storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the recording in the specified bucket.
allow_api_access
boolean
Controls whether the recording will be accessible using Daily's API.
allow_streaming_from_bucket
boolean
Specifies which Content-Disposition response header the recording link retrieved from the access-link REST API endpoint will have. If allow_streaming_from_bucket is false, the header will be Content-Dispostion: attachment. If allow_streaming_from_bucket is true, the header will be Content-Disposition: inline. To play the recording link directly in the browser or embed it in a video player, set this property to true.
Default: false
enable_terse_logging
boolean
Reduces the volume of log messages. This feature should be enabled when there are more than 200 participants in a meeting to help improve performance.

See our guides for supporting large experiences for additional instruction.
Default: false
auto_transcription_settings
object
PAY-AS-YOU-GO
Options to use when auto_start_transcription is true. See startTranscription() for available options.
enable_transcription_storage
boolean
Live transcriptions generated can be saved as WebVTT. This flag controls if transcription started with startTranscription() should be saved or not.
Default: false
transcription_bucket
object
Configures an S3 bucket in which to store transcriptions. See the S3 bucket guide for more information.
bucket_name
string
The name of the Amazon S3 bucket to use for transcription storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the transcription in the specified bucket.
allow_api_access
boolean
Whether the transcription should be accessible using Daily's API.
recordings_template
string
Cloud recordings are stored in either Daily's S3 bucket or the customer's own S3 bucket. By default recordings are stored as {domain_name}/{room_name}/{epoch_time}. Sometimes, the use case may call for custom recording file names to be used (for example, if you'd like to enforce the presence of the .mp4 extension in the file name).

recordings_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in milliseconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting recorded (optional)
mtg_session_id: The ID of the meeting session which is getting recorded (optional)
instance_id: The instance ID of the recording (optional)
recording_id: The recording ID of the recording (optional)
The restrictions for defining a recording template are as follows:

The epoch_time tag is mandatory to ensure the recording file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
.mp4 is the only valid extension
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.
transcription_template
string
transcriptions can be stored in either Daily's S3 bucket or the customer's own S3 bucket. By default transcriptions are stored as {domain_name}/{room_name}/{epoch_time}.vtt. Sometimes, the use case may call for custom file path to be used (for example, if you'd like to map stored transcription to mtgSessionId).

transcription_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in seconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting transcribed (optional)
mtg_session_id: The ID of the meeting session which is getting transcribed (optional)
instance_id: The instance ID of the transcription (optional)
transcript_id: The transcript ID of the transcription (optional)
The restrictions for defining a transcription template are as follows:

The epoch_time tag is mandatory to ensure the transcription file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.vtt.
enable_dialout
boolean
Allow dialout API from the room.
Default: false
dialout_config
object
Allow configuring dialout behaviour.
allow_room_start
boolean
Setting this to true allows starting the room and initiating the dial-out even though there is no user present in the room. By default, initiating a dial-out via the REST API fails when the corresponding room is empty (without any participant).
Default: false
dialout_geo
string
The region where SFU is selected to start the room. default is taken from room geo else from domain geo and if both are not defined us-west-2 is take as default.
max_idle_timeout_sec
number
Number of seconds where dialout user can be alone in the room. dialout user can start the room and can remain in the room alone waiting for other participant for this duration, also when all the web users leave the room, room is automatically closed, this property allows dialout user to remain in room after all web users leave the room.
Default: 0
streaming_endpoints
array
An array of stream endpoint configuration objects, which allows configurations to be pre-defined without having to pass them into startLiveStreaming() at runtime. For example, an RTMP endpoint can be set up for YouTube as a streaming_endpoints configuration along with another configuration for HLS storage.

HLS output can only be stored on a customer's S3, not in Daily's storage infrastructure. The stream configuration defines which S3 bucket to store the HLS output. (See the S3 bucket guide for more information.)

Example:

JSON
Copy to clipboard

{
  "properties": {
    // ... add additional room properties here
    "streaming_endpoints": [
      {
        "name": "rtmp_youtube",
        "type": "rtmp",
        "rtmp_config": {
          "url": "rtmps://exampleYouTubeServer.com:443/stream"
        }
      },

      {
        "name": "rtmp_ivs",
        "type": "rtmp",
        "rtmp_config": {
          "url": "rtmps://811111111111.global-contribute.live-video.net:443/app/"
        }
      },

      {
        "name": "hls_akamai",
        "type": "hls",
        "hls_config": {
        "save_hls_recording": true/false,
          "storage": {
            "bucket_name": "daily-hls-streams",
            "bucket_region": "us-west-2",
            "assume_role_arn": "arn:aws:iam::999999999999:role/DailyS3AccessRole",
            "path_template": "testHarness/{live_streaming_id}/{instance_id}"
          },
          "variant" : [
              {
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "bitrate": 3500,
                "iframe_only": false
              },
              {
                "width": 1280,
                "height": 720,
                "fps": 30,
                "bitrate": 2500,
                "iframe_only": false
              },
              {
                "width": 640,
                "height": 360,
                "fps": 30,
                "bitrate": 780,
                "iframe_only": true
              }
          ]
        }
      }
    ]
  }
}

To reset the streaming_endpoints property, pass null instead of an array.

When calling startLiveStreaming(), the pre-defined streaming_endpoints name can be used:

JavaScript
Copy to clipboard
await callObject.startLiveStreaming({
  endpoints: [{"endpoint":"rtmp_youtube"},{"endpoint":"rtmp_fb"}],
  width: 1280,
  height: 720,
});

Properties:
permissions
object
Specifies the initial default permissions for a non-meeting-owner participant joining a call.

Each permission (i.e. each of the properties listed below) can be configured in the meeting token, the room, and/or the domain, in decreasing order of precedence.

Participant admins (those with the 'participants' value in their canAdmin permission) can also change participants' permissions on the fly during a call using updateParticipant() or updateParticipants().
hasPresence
boolean
Whether the participant appears as "present" in the call, i.e. whether they appear in participants().
canSend
boolean | array
Which types of media a participant should be permitted to send.

Can be:

An Array containing any of 'video', 'audio', 'screenVideo', and 'screenAudio'
true (meaning "all")
false (meaning "none")
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
boolean | array
Which admin tasks a participant is permitted to do.

Can be:

An array containing any of 'participants', 'streaming', or 'transcription'
true (meaning "all")
false (meaning "none")
Default: <not set>
Example requests

Create a randomly named room that expires in an hour

Here's how you might create a room with an auto-generated name, set to expire in an hour. This is a pretty common use case. For example, maybe you're creating rooms on demand to use for customer support or account verification. You don't need to set the room's privacy, because you won't be sharing the room URL other than within your own UI, and you won't be re-using the room. It is worth setting the room exp, just so that the room is auto-deleted and you don't end up with a huge number of live rooms.


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d \
     '{"properties":{"exp":'`expr $(date +%s) + 3600`'}}' \
     https://api.daily.co/v1/rooms/
        
If you're writing API calls in JavaScript, note that exp and nbf are unix timestamps expressed in seconds, not in milliseconds. You will need to divide JavaScript timestamps by 1,000 to turn them into unix timestamps. For example, you probably want to use some variant of Math.floor(Date.now()/1000) as a base value when creating near-future expiration timestamps. Don't just use Date.now().
Create a private room with a human-readable name and devices turned off at start

Here's how you might create a room with a human-readable name, and privacy set to private, and with the default behavior of everyone's camera and mic turned off initially. You can create meeting tokens to allow access to this room (Learn more in our guide to room access control).


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d \
     '{"name": "getting-started-webinar",
       "privacy": "private",
       "properties" : {
          "start_audio_off":true,
          "start_video_off":true}}' \
     https://api.daily.co/v1/rooms/
        
When a room object is returned by an API call, only configuration options that differ from the defaults are included in the config struct.*

GET /rooms/:name
A GET request to /rooms/:name retrieves a room object.

When a room object is returned by an API call, only configuration options that differ from the defaults are included in the config struct.

Heads up!
See room configuration for a discussion of the room object and a table of all room configuration options.
Path params

room_name
string
Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     https://api.daily.co/v1/rooms/w2pp2cf4kltgFACPKXmX

GET/rooms/:name/presence
A GET request to /rooms/:name/presence retrieves presence data about a specific room.

This endpoint provides a snapshot of the presence of participants in a given room.

Path params

room_name
The name of the room
Query params

limit
Sets the number of participants returned.
userId
Returns presence for the user with the given userId, if available. The userId is specified via a meeting token.
userName
Returns presence for the user with the given name, if available.
Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     https://api.daily.co/v1/rooms/w2pp2cf4kltgFACPKXmX/presence

POST /rooms/:room
A POST request to /rooms/:name modifies a room object's privacy or configuration properties.

Returns a room object if the operation is successful.

In the case of an error, returns an HTTP error with information about the error in the response body.

Path params

name
string
Defaults to a randomly generated string A room name can include only the uppercase and lowercase ascii letters, numbers, dash and underscore. In other words, this regexp detects an invalid room name: /[^A-Za-z0-9_-]/.

The room name cannot exceed 128 characters. You'll get an error if you try to create a room with a name that's too long.
Body params

privacy

privacy
string
Determines who can access the room.
Options: "public","private"
Default: "public"
properties

nbf
integer
"Not before". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in this room before this time.
exp
integer
"Expires". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in this room after this time.

More resources:

Add advanced security to video chats with the Daily API
max_participants
integer
PAY-AS-YOU-GO
How many people are allowed in a room at the same time.

⚠️ Contact us if you need to set the limit above 200.
Default: 200
enable_people_ui
boolean
Determines if Daily Prebuilt displays the People UI. When set to true, a People button in the call tray reveals a People tab in the call sidebar. The tab lists all participants, and next to each name indicates audio status and an option to pin the participant. When enable_people_ui is set to false, the button and tab are hidden.

⚠️ Has no effect on custom calls built on the Daily call object.
enable_cpu_warning_notifications
boolean
Determines if Daily Prebuilt displays CPU warning notifications. When set to true, snackbar notifications appear when high CPU usage is detected. When set to false, these notifications are hidden.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_pip_ui
boolean
Sets whether the room can use Daily Prebuilt's Picture in Picture controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle the Picture in Picture feature.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_emoji_reactions
boolean
Determines if Daily Prebuilt displays the Emoji Reactions UI. When set to true, a Reactions button appears in the call tray. This button allows users to select and send a reaction into the call. When set to false, the Reactions button is hidden and the feature is disabled.

Usage: This feature is a good fit for meetings when a host or presenter would benefit from receiving nonverbal cues from the audience. It's also great to keep meetings fun.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_hand_raising
boolean
Sets whether the participants in the room can use Daily Prebuilt's hand raising controls. When set to true, an additional button will be available in Daily Prebuilt's UI to toggle a hand raise.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
enable_prejoin_ui
boolean
Determines whether participants enter a waiting room with a camera, mic, and browser check before joining a call.

⚠️ You must be using Daily Prebuilt to use enable_prejoin_ui.
enable_live_captions_ui
boolean
Sets whether participants in a room see a closed captions button in their Daily Prebuilt call tray. When the closed caption button is clicked, closed captions are displayed locally.

When set to true, a closed captions button appears in the call tray. When set to false, the closed captions button is hidden from the call tray.

Note: Transcription must be enabled for the room or users must have permission to start transcription for this feature to be enabled. View the transcription guide for more details.

⚠️ You must be using Daily Prebuilt to use enable_live_captions_ui.
enable_network_ui
boolean
Determines whether the network button, and the network panel it reveals on click, appears in this room.

⚠️ You must be using Daily Prebuilt to use enable_network_ui.
enable_noise_cancellation_ui
boolean
Determines whether Daily Prebuilt displays noise cancellation controls. When set to true, a participant can enable microphone noise cancellation during a Daily Prebuilt call. ⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object. To learn more about adding noise cancellation to a custom application, see the updateInputSettings() docs.
enable_breakout_rooms
boolean
Sets whether Daily Prebuilt’s breakout rooms feature is enabled. When set to true, an owner in a Prebuilt call can create breakout rooms to divide participants into smaller, private groups.

⚠️ You must be using Daily Prebuilt to use enable_breakout_rooms.

⚠️ This property is in beta.
enable_knocking
boolean
Turns on a lobby experience for private rooms. A participant without a corresponding meeting token can request to be admitted to the meeting with a "knock", and wait for the meeting owner to admit them.
enable_screenshare
boolean
Sets whether users in a room can screen share during a session. This property cannot be changed after a session starts. For dynamic control over permissions, use the updateParticipant() method to control user permissions.
Default: true
enable_video_processing_ui
boolean
Determines whether Daily Prebuilt displays background blur controls. When set to true, a participant can enable blur during a Daily Prebuilt call.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: true
enable_chat
boolean
This property is one of multiple ways to add chat to Daily video calls.
Default: false
enable_shared_chat_history
boolean
When enabled, newly joined participants in Prebuilt calls will request chat history from remote peers, in order to view chat messages from before they joined.
Default: true
start_video_off
boolean
Disable the default behavior of automatically turning on a participant's camera on a direct join() (i.e. without startCamera() first).
Default: false
start_audio_off
boolean
Disable the default behavior of automatically turning on a participant's microphone on a direct join() (i.e. without startCamera() first).
Default: false
owner_only_broadcast
boolean
In Daily Prebuilt, only the meeting owners will be able to turn on camera, unmute mic, and share screen.

See setting up calls.
Default: false
enable_recording
string
Jump to recording docs.
Options: "cloud","local","raw-tracks","<not set>"
Default: <not set>
eject_at_room_exp
boolean
If there's a meeting going on at room exp time, end the meeting by kicking everyone out. This behavior can be overridden by setting eject properties of a meeting token.
Default: false
eject_after_elapsed
integer
Eject a meeting participant this many seconds after the participant joins the meeting. You can use this is a default length limit to prevent long meetings. This can be overridden by setting eject properties of a meeting token.
enable_advanced_chat
boolean
Property that gives end users a richer chat experience. This includes:

Emoji reactions to chat messages
Emoji picker in the chat input form
Ability to send a Giphy chat message
⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
Default: false
enable_hidden_participants
boolean
When enabled, non-owner users join a meeting with a hidden presence, meaning they won't appear as a named participant in the meeting and have no participant events associated to them. Additionally, these participants can only receive media tracks from owner participants.

Hidden participants can be tracked using the participantCounts() method. Hidden participants do not have entries in the participants() method return value.

When used with Daily Prebuilt, hidden participants are included in the participant count available in the UI; however, are not included in the People panel and can only read chat messages.

This property should be used to support hosting large meetings. See our guide on interactive live streaming for additional instruction.
Default: false
enable_mesh_sfu
boolean
Configures a room to use multiple SFUs for a call's media. This feature enables calls to scale to large sizes and to reduce latency between participants. It is recommended specifically for interactive live streaming.

See our guide for interactive live streaming for additional instruction.
sfu_switchover
number
Dictates the participant count after which room topology automatically switches from Peer-to-Peer (P2P) to Selective Forwarding Unit (SFU) mode, or vice versa.

For example, if sfu_switchover is set to 2 and the current network topology is P2P, the topology will switch to SFU mode when the third participant joins the call. If the current topology is SFU, it will switch to P2P mode when the participant count decreases from 2 to 1.

We recommend specifying an integer value for this property except for cases where you would like the room to switch to SFU mode as soon as the first participant joins. In this case, set sfu_switchover to 0.5.

See our guide about video call architecture for additional information.
Default: 0.5
enable_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_adaptive_simulcast to true will enable Daily Adaptive Bitrate for 1:1 calls.
Default: true
enable_multiparty_adaptive_simulcast
boolean
Configures a domain or room to use Daily Adaptive Bitrate. When enabled, along with configuring the client to allowAdaptiveLayers, the Daily client will continually adapt send settings to the current network conditions. allowAdaptiveLayers is true by default; if you haven't modified that setting, then setting enable_multiparty_adaptive_simulcast to true will enable Daily Adaptive Bitrate for multi-party calls. To use this feature, enable_adaptive_simulcast must also be set to true.
Default: false
enforce_unique_user_ids
boolean
Configures a domain or room to disallow multiple participants from having the same user_id. This feature can be enabled to prevent users from "sharing" meeting tokens. When enabled, a participant joining or reconnecting to a meeting will cause existing participants with the same user_id to be ejected.
Default: false
experimental_optimize_large_calls
boolean
Enables Daily Prebuilt to support group calls of up to 1,000 participants and owner only broadcast calls of up to 100K participants.

When set to true, Daily Prebuilt will:

Automatically mute the local user on joining
Update grid view to show a maximum of 12 users in the grid at a time
Allow only 16 users to be unmuted at the same time. When more than 16 users are unmuted, the oldest active speaker will be automatically muted.
See our guide on large real-time calls for additional instruction.

⚠️ This flag only applies to Daily Prebuilt. It has no effect when building custom video applications with the Daily call object.
lang
string
The default language of the Daily prebuilt video call UI, for this room.

Setting the language at the room level will override any domain-level language settings you have.

Read more about changing prebuilt UI language settings.

* Norwegian "no" and Russian "ru" are only available in the new Daily Prebuilt.
Options: "da","de","en","es","fi","fr","it","jp","ka","nl","no","pt","pt-BR","pl","ru","sv","tr","user"
Default: en
meeting_join_hook
string
Sets a URL that will receive a webhook when a user joins a room. Default is NULL. Character limit for webhook URL is 255.

⚠️ In place of the meeting_join_hook, we recommend setting up a webhook and listening for the participant.joined event.
geo
string
Daily uses signaling servers to manage all of the participants in a given call session. In an SFU/server mode call, the server will send and receive all audio and video from each participant. In a peer-to-peer call, each participant sends media directly to and from each other peer, but a signaling server still manages call state.

Daily runs servers in several different AWS regions to minimize latency for users around the world. The job of 'picking' a call server is handled when the first participant joins a room. The first participant's browser connects to a call server using Amazon's Route 53 DNS resolution, which chooses a server in the region closest to them.

This isn't always optimal. For example, if one person joins in London, and then ten more people join from Cape Town, the call will still be hosted out of eu-west-2 . The majority of the participants will have higher latency to the server than if one of them had joined first and the call was being hosted in af-south-1. In cases like this, you may want to configure your domain (or a specific room) to always choose a call server in a specific AWS region.

Available regions:

"af-south-1" (Cape Town)
"ap-northeast-2" (Seoul)
"ap-southeast-1" (Singapore)
"ap-southeast-2" (Sydney)
"ap-south-1" (Mumbai)
"eu-central-1" (Frankfurt)
"eu-west-2" (London)
"sa-east-1" (São Paulo)
"us-east-1" (N. Virginia)
"us-west-2" (Oregon)
Default: NULL
rtmp_geo
string
Used to select the region where an RTMP stream should originate. In cases where RTMP streaming services aren't available in the desired region, we'll attempt to fall back to the default region based on the SFU being used for the meeting.

Available regions:

"us-west-2" (Oregon)
"eu-central-1" (Frankfurt)
"ap-south-1" (Mumbai)
The default regions are grouped based on the SFU region like so:

RTMP region "us-west-2" includes SFU regions: "us-west-2", "us-east-1", "sa-east-1"
RTMP region "eu-central-1" includes SFU regions: "eu-central-1", "eu-west-2", "af-south-1"
RTMP region "ap-south-1" includes SFU regions: "ap-southeast-1", "ap-southeast-2", "ap-northeast-2", "ap-south-1"
Default: The closest available region to the SFU region used by the meeting.
disable_rtmp_geo_fallback
boolean
Disable the fall back behavior of rtmp_geo. When rtmp_geo is set, we first try to connect to a media server in desired region. If a media server is not available in the desired region, we fall back to default region based on SFU's region. This property disables this automatic fall back. When this property is set, we will trigger a recording/streaming error event when media worker is unavailable. Also, the client should retry recording/streaming.
Default: false
recordings_bucket
object
Configures an S3 bucket in which to store recordings. See the S3 bucket guide for more information.

Properties:
bucket_name
string
The name of the Amazon S3 bucket to use for recording storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the recording in the specified bucket.
allow_api_access
boolean
Controls whether the recording will be accessible using Daily's API.
allow_streaming_from_bucket
boolean
Specifies which Content-Disposition response header the recording link retrieved from the access-link REST API endpoint will have. If allow_streaming_from_bucket is false, the header will be Content-Dispostion: attachment. If allow_streaming_from_bucket is true, the header will be Content-Disposition: inline. To play the recording link directly in the browser or embed it in a video player, set this property to true.
Default: false
enable_terse_logging
boolean
Reduces the volume of log messages. This feature should be enabled when there are more than 200 participants in a meeting to help improve performance.

See our guides for supporting large experiences for additional instruction.
Default: false
auto_transcription_settings
object
PAY-AS-YOU-GO
Options to use when auto_start_transcription is true. See startTranscription() for available options.
enable_transcription_storage
boolean
Live transcriptions generated can be saved as WebVTT. This flag controls if transcription started with startTranscription() should be saved or not.
Default: false
transcription_bucket
object
Configures an S3 bucket in which to store transcriptions. See the S3 bucket guide for more information.
bucket_name
string
The name of the Amazon S3 bucket to use for transcription storage.
bucket_region
string
The region which the specified S3 bucket is located in.
assume_role_arn
string
The Amazon Resource Name (ARN) of the role Daily should assume when storing the transcription in the specified bucket.
allow_api_access
boolean
Whether the transcription should be accessible using Daily's API.
recordings_template
string
Cloud recordings are stored in either Daily's S3 bucket or the customer's own S3 bucket. By default recordings are stored as {domain_name}/{room_name}/{epoch_time}. Sometimes, the use case may call for custom recording file names to be used (for example, if you'd like to enforce the presence of the .mp4 extension in the file name).

recordings_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in milliseconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting recorded (optional)
mtg_session_id: The ID of the meeting session which is getting recorded (optional)
instance_id: The instance ID of the recording (optional)
recording_id: The recording ID of the recording (optional)
The restrictions for defining a recording template are as follows:

The epoch_time tag is mandatory to ensure the recording file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
.mp4 is the only valid extension
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.
transcription_template
string
transcriptions can be stored in either Daily's S3 bucket or the customer's own S3 bucket. By default transcriptions are stored as {domain_name}/{room_name}/{epoch_time}.vtt. Sometimes, the use case may call for custom file path to be used (for example, if you'd like to map stored transcription to mtgSessionId).

transcription_template is made up of a replacement string with prefixes, suffixes, or both. The currently supported replacements are:

epoch_time: The epoch time in seconds (mandatory)
domain_name: Your Daily domain (optional)
room_name: The name of the room which is getting transcribed (optional)
mtg_session_id: The ID of the meeting session which is getting transcribed (optional)
instance_id: The instance ID of the transcription (optional)
transcript_id: The transcript ID of the transcription (optional)
The restrictions for defining a transcription template are as follows:

The epoch_time tag is mandatory to ensure the transcription file name is unique under all conditions
The maximum size of the template is 1024 characters
Each replacement parameter should be placed within a curly bracket (e.g., {domain_name})
Only alphanumeric characters (0-9, A-Z, a-z) and ., /, -, _ are valid within the template
Examples

Example domain: "myDomain"
Example room: "myRoom"
Example 1:

Template: myprefix-{domain_name}-{epoch_time}.mp4
Resulting file name: myprefix-myDomain-1675842936274.mp4
Example 2:

Template: {room_name}/{instance_id}/{epoch_time}
Resulting room name: myRoom/d529cd2f-fbcc-4fb7-b2c0-c4995b1162b6/1675842936274
Default: {domain_name}/{room_name}/{epoch_time}.vtt.
enable_dialout
boolean
Allow dialout API from the room.
Default: false
dialout_config
object
Allow configuring dialout behaviour.
allow_room_start
boolean
Setting this to true allows starting the room and initiating the dial-out even though there is no user present in the room. By default, initiating a dial-out via the REST API fails when the corresponding room is empty (without any participant).
Default: false
dialout_geo
string
The region where SFU is selected to start the room. default is taken from room geo else from domain geo and if both are not defined us-west-2 is take as default.
max_idle_timeout_sec
number
Number of seconds where dialout user can be alone in the room. dialout user can start the room and can remain in the room alone waiting for other participant for this duration, also when all the web users leave the room, room is automatically closed, this property allows dialout user to remain in room after all web users leave the room.
Default: 0
streaming_endpoints
array
An array of stream endpoint configuration objects, which allows configurations to be pre-defined without having to pass them into startLiveStreaming() at runtime. For example, an RTMP endpoint can be set up for YouTube as a streaming_endpoints configuration along with another configuration for HLS storage.

HLS output can only be stored on a customer's S3, not in Daily's storage infrastructure. The stream configuration defines which S3 bucket to store the HLS output. (See the S3 bucket guide for more information.)

Example:

JSON
Copy to clipboard

{
  "properties": {
    // ... add additional room properties here
    "streaming_endpoints": [
      {
        "name": "rtmp_youtube",
        "type": "rtmp",
        "rtmp_config": {
          "url": "rtmps://exampleYouTubeServer.com:443/stream"
        }
      },

      {
        "name": "rtmp_ivs",
        "type": "rtmp",
        "rtmp_config": {
          "url": "rtmps://811111111111.global-contribute.live-video.net:443/app/"
        }
      },

      {
        "name": "hls_akamai",
        "type": "hls",
        "hls_config": {
        "save_hls_recording": true/false,
          "storage": {
            "bucket_name": "daily-hls-streams",
            "bucket_region": "us-west-2",
            "assume_role_arn": "arn:aws:iam::999999999999:role/DailyS3AccessRole",
            "path_template": "testHarness/{live_streaming_id}/{instance_id}"
          },
          "variant" : [
              {
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "bitrate": 3500,
                "iframe_only": false
              },
              {
                "width": 1280,
                "height": 720,
                "fps": 30,
                "bitrate": 2500,
                "iframe_only": false
              },
              {
                "width": 640,
                "height": 360,
                "fps": 30,
                "bitrate": 780,
                "iframe_only": true
              }
          ]
        }
      }
    ]
  }
}

To reset the streaming_endpoints property, pass null instead of an array.

When calling startLiveStreaming(), the pre-defined streaming_endpoints name can be used:

JavaScript
Copy to clipboard
await callObject.startLiveStreaming({
  endpoints: [{"endpoint":"rtmp_youtube"},{"endpoint":"rtmp_fb"}],
  width: 1280,
  height: 720,
});

Properties:
permissions
object
Specifies the initial default permissions for a non-meeting-owner participant joining a call.

Each permission (i.e. each of the properties listed below) can be configured in the meeting token, the room, and/or the domain, in decreasing order of precedence.

Participant admins (those with the 'participants' value in their canAdmin permission) can also change participants' permissions on the fly during a call using updateParticipant() or updateParticipants().
hasPresence
boolean
Whether the participant appears as "present" in the call, i.e. whether they appear in participants().
canSend
boolean | array
Which types of media a participant should be permitted to send.

Can be:

An Array containing any of 'video', 'audio', 'screenVideo', and 'screenAudio'
true (meaning "all")
false (meaning "none")
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
boolean | array
Which admin tasks a participant is permitted to do.

Can be:

An array containing any of 'participants', 'streaming', or 'transcription'
true (meaning "all")
false (meaning "none")
Default: <not set>
Example requests

Change a room's privacy


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"privacy":"private"}' \
     https://api.daily.co/v1/rooms/hello
        
Change a room's max_participants property


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d \
     '{"properties":{"max_participants":20}}' \
     https://api.daily.co/v1/rooms/hello
        
Change a room's max_participants property back to default


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d \
     '{"properties":{"max_participants":null}}' \
     https://api.daily.co/v1/rooms/hello

DELETE /rooms/:name
A DELETE request to /rooms/:name deletes a room.

If the requested room is found and deleted, this API endpoint returns two fields in the response body: deleted (set to true), and the room name.

If the room is not found (and, therefore, cannot be deleted) the endpoint returns an HTTP 404 error.

If the room exists but its exp time has passed, the endpoint returns an HTTP error exactly as above, but with the addition of a deleted field, set to true. In general, expired rooms are treated by API endpoints as having been implicitly deleted. And, in fact, they will eventually be deleted by a collector process that runs periodically. But in rare cases you may want to know that your API call has deleted an expired room.

Path params

name
string
Defaults to a randomly generated string A room name can include only the uppercase and lowercase ascii letters, numbers, dash and underscore. In other words, this regexp detects an invalid room name: /[^A-Za-z0-9_-]/.

The room name cannot exceed 128 characters. You'll get an error if you try to create a room with a name that's too long.
Example requests

Delete a room


Request

200 OK
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XDELETE 
     https://api.daily.co/v1/rooms/room-0253
        
Room not found to delete


Request

404
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XDELETE 
     https://api.daily.co/v1/rooms/room-name-with-typo

POST
/rooms/:name/send-app-message

Sends a message to participants within a room.

Messages are delivered to participants currently in the call. They are not stored. If a recipient is not in the call when the message is sent, the recipient will never receive the message.

In the case of an error, returns an HTTP error with information about the error in the response body.

You can listen for these messages by installing a handler for the app-message event.

Path params

name
string
The name of the room.
Body params

data
object
A javascript object that can be serialized into JSON. Data sent must be within the 4kb size limit.
recipient
string
Determines who will recieve the message. It can be either a participant session_id, or *. The * value is the default, and means that the message is a "broadcast" message intended for all participants.
Default: *
Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"data":{"test": 1}, "recipient": "*"}' \
     https://api.daily.co/v1/rooms/hello/send-app-message

GET /rooms/:name/get-session-data
Gets the meeting session data.

In the case of an error, returns an HTTP error with information about the error in the response body.

See the documentation for the in-call setMeetingSessionData method for more information about how meeting session data works.

Path params

name
string
The name of the room.
Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     https://api.daily.co/v1/rooms/hello/get-session-data

POST
/rooms/:name/set-session-data

Sets the meeting session data, which will be synced to all participants within a room.

In the case of an error, returns an HTTP error with information about the error in the response body.

See the documentation for the in-call setMeetingSessionData method for more information about how meeting session data works.

Path params

name
string
The name of the room.
Body params

data
object
A javascript object that can be serialized into JSON. Defaults to {}.
mergeStrategy
string
replace to replace the existing meeting session data object or shallow-merge to merge with it.
Options: "replace","shallow-merge"
Default: replace
keysToDelete
array
Optional list of keys to delete from the existing meeting session data object when using shallow-merge.
Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"data":{"hello": "world"}, "mergeStrategy": "shallow-merge", "keysToDelete": ["one", "two"]}' \
     https://api.daily.co/v1/rooms/hello/set-session-data

POST /rooms/:name/eject

Ejects participants from an ongoing meeting. In the case of success, the ids of ejected participants are returned in ejectedIds. If one or more participants are not found, the call is still considered successful - examine the ejectedIds value to determine exactly which participants were ejected.

In the case of an error, returns an HTTP error with information about the error in the response body.

The participants to be ejected may be identified by participant id or by the user_id specified in a meeting token. If ban is true, any user_id values given are remembered while the meeting is active, and participants are prevented from (re)joining with that user_id. (The lists of "banned" user_ids are not guaranteed to persist forever - they are stored in memory in running servers and some operations, such as software updates, reset the lists. But for most practical purposes, this mechanism may be used to prevent unwanted users from rejoining a meeting.)

See the documentation for the in-call updateParticipant method for an alternative mechanism for ejecting participants.

Path params

name
string
The name of the room.
Body params

ids
array
List of participant ids (max 100) to eject from the existing meeting session.
user_ids
array
List of user_ids (max 100) to eject from the existing meeting session.
ban
boolean
If true, participants are prevented from (re)joining with the given user_ids.
Default: false
Example requests


Request

200 OK

404 not found
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"ids": ["8148d9f0-11aa-46e4-8bb2-1c135679bf87"]}' \
     https://api.daily.co/v1/rooms/hello/eject

POST /rooms/:name/update-permissions

Updates permissions for participants in an ongoing meeting.

In the case of an error, returns an HTTP error with information about the error in the response body.

See the documentation for the in-call updateParticipant method for more details about participant permissions.

Path params

name
string
The name of the room.
Body params

data
object
Each key-value pair in the data object defines a set of permission updates to apply to a given participant. To specify a specific participant, use the participant id as the key in the data object, with the value being the object described below. You can also apply an update to all participants except those specified explicitly by using the key "*" instead of a participant id.

The value of each pair is an object containing some or all of the following properties:

Attribute Name	Type	Description	Example
hasPresence	boolean	Determines whether the participant is "present" or "hidden"	false
canSend	boolean or array	Array of strings identifying which types of media the participant can send or a boolean to grant/revoke permissions for all media types.	['video', 'audio']
canReceive	object	Object specifying which media the participant should be permitted to receive. See here for canReceive object format.	{ base: false }
canAdmin	boolean or array	Array of strings identifying which types of admin tasks the participant can do or a boolean to grant/revoke permissions for all types.	['participants']
When you provide one or more of canSend, hasPresence, or canAdmin, the provided permission completely overwrites whatever value the participant previously had for that permission. When you provide canReceive, the provided sub-fields—base, byUserId, or byParticipantId—overwrites the previous values of the corresponding canReceive sub-fields. If you omit any permission field, the corresponding participant permission won't be changed.

See the documentation for the in-call updateParticipant method for the allowed permissions values.

Example requests


Request

200 OK

404 not found
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"data": {"8148d9f0-11aa-46e4-8bb2-1c135679bf87": {"hasPresence": true}}}' \
     https://api.daily.co/v1/rooms/hello/update-permissions

Recordings
PAY-AS-YOU-GO
You can start, update, or stop a recording with the Daily API.

This set of endpoints can start "cloud" or "raw-tracks" recordings. It will default to "cloud" recordings. You can use the recordings endpoints to get more information about the status of a given recording.

The endpoints are mostly equivalent to the startRecording(), updateRecording(), and stopRecording() calls found in our daily-js library.


POST /rooms/:name/recordings/start

Starts a recording with a given layout configuration.

Multiple recording sessions (up to max_streaming_instances_per_room on your Daily domain) can be started by specifying a unique instanceId. Each instance can have a different layout, participants, lifetime, and update rules.

A 503 status code may be returned if there are not enough workers available. In this case, you may retry the request again.

Contact us to configure max_streaming_instances_per_room for your domain.

You can pass configuration properties to this endpoint to control the look and feel of the recording, including the type of recording you would like to start. In order to start a "raw-tracks" recording, you must be using a custom s3 bucket configuration.

The options currently include:

height, width: Can be specified to control the resolution of the live stream. The value must be even, i.e., a multiple of 2.
backgroundColor: Specifies the background color of the stream, formatted as #rrggbb or #aarrggbb string.
fps: Specifies the video frame rate per second.
videoBitrate: Specifies the video bitrate in kilobits per second (kbps) to use for video output. Value can range between 10 and 10000. If not specified, the following bitrate values will be used for each given resolution:

1080p: 5000
720p: 3000
480p: 2000
360p: 1000
audioBitrate: Specifies the audio bitrate in kilobits per second (kbps) to use for audio output. Value can range between 10 and 320.
minIdleTimeOut: Amount of time in seconds to wait before ending a recording or live stream when the room is idle (e.g. when all users have muted video and audio). Default: 300 (seconds). Note: Once the timeout has been reached, it typically takes an additional 1-3 minutes for the recording or live stream to be shut down.
maxDuration: maximum duration in seconds after which recording/streaming is forcefully stopped. Defaults: 10800 seconds (3 hours) for recordings, 86400 seconds (24 hours) for streaming. This is a preventive circuit breaker to prevent billing surprises in case a user starts recording/streaming and leaves the room.
instanceId: UUID for a streaming or recording session. Used when multiple streaming or recording sessions are running for single room. Default: "c3df927c-f738-4471-a2b7-066fa7e95a6b". Note: "c3df927c-f738-4471-a2b7-066fa7e95a6b" is reserved internally; do not use this UUID.
type: specify type of recording ("cloud", "raw-tracks", "local") to start. Particular recording type must be enabled for the room or domain with enable_recording property.
layout: an object specifying the way participants’ videos are laid out in the live stream. A preset key with one of the following values must be provided:

'default': This is the default grid layout, which renders participants in a grid, or in a vertical grid to the right, if a screen share is enabled. Optionally, a max_cam_streams integer key can be provided to specify how many cameras to include in the grid. The default value is 20, which is also the maximum number of cameras in a grid. The maximum may be increased at a later date.
'audio-only': This layout creates an audio only cloud recording. Video will not be a part of the recording.
'single-participant': Use this layout to limit the audio and video to be streamed to a specific participant. The selected participant’s session ID must be specified via a session_id key.
'active-participant': This layout focuses on the current speaker, and places up to 9 other cameras to the right in a vertical grid in the order in which they last spoke.
'portrait': Allows for mobile-friendly layouts. The video will be forced into portrait mode, where up to 2 participants will be shown. An additional variant key may be specified. Valid values are:
'vertical' for a vertical grid layout (the default)
'inset'for having one participant's video take up the entire screen, and the other inset in a smaller rectangle. Participants' videos are scaled and cropped to fit the entire available space. Participants with the is_owner flag are shown lower in the grid (vertical variant), or full screen (inset variant).
'raw-tracks-audio-only': record only the audio tracks for raw-tracks recording. (NOTE: applicable only for raw-tracks recording)

'custom': Allows for custom layouts. (See below.)
Path params

name
string
The name of the room.
Body params

width
number
Property that specifies the output width of the given stream.
height
number
Property that specifies the output height of the given stream.
fps
number
Property that specifies the video frame rate per second.
videoBitrate
number
Property that specifies the video bitrate for the output video in kilobits per second (kbps).
audioBitrate
number
Property that specifies the audio bitrate for the output audio in kilobits per second (kbps).
minIdleTimeOut
number
Amount of time in seconds to wait before ending a recording or live stream when the room is idle (e.g. when all users have muted video and audio). Default: 300 (seconds). Note: Once the timeout has been reached, it typically takes an additional 1-3 minutes for the recording or live stream to be shut down.
maxDuration
number
Maximum duration in seconds after which recording/streaming is forcefully stopped. Default: `15000` seconds (3 hours). This is a preventive circuit breaker to prevent billing surprises in case a user starts recording/streaming and leaves the room.
backgroundColor
string
Specifies the background color of the stream, formatted as #rrggbb or #aarrggbb string.
instanceId
string
UUID for a streaming or recording session. Used when multiple streaming or recording sessions are running for single room.
type
string
The type of recording that will be started.
Options: "cloud","raw-tracks"
Default: cloud
layout
object
An object specifying the way participants’ videos are laid out in the live stream. See given layout configs for description of fields. Preset must be defined.
Default Layout

preset
string
Options: "default"
max_cam_streams
number
Single Participant Layout

preset
string
Options: "single-participant"
session_id
string
Active Participant Layout

preset
string
Options: "active-participant"
Portrait Layout

preset
string
Options: "portrait"
variant
string
Options: "vertical","inset"
max_cam_streams
number
Custom Layout

preset
string
Options: "custom"
composition_id
string
composition_params
object
session_assets
object
Custom video layouts with VCS baseline composition

The baseline composition option is only available for cloud recordings and live streaming.
Daily offers a "baseline" composition option via the "custom" layout preset for customizing your video layouts while recording. This option allows for even more flexibility while using Daily's recording API.

Review our Video Component System (VCS) guide or VCS Simulator for additional information and code examples.
Many VCS properties use a "grid unit". The grid unit is a designer-friendly, device-independent unit. The default grid size is 1/36 of the output's minimum dimension. In other words, 1gu = 20px on a 720p stream and 30px on a 1080p stream. Learn more about grid units in our [VCS SDK docs](/reference/vcs/layout-api#the-grid-unit).

composition_params

mode
string
Sets the layout mode. Valid options:

single: Show a single full-screen video.
split: Show the first two participants side-by-side.
grid: Show up to 20 videos in a grid layout.
dominant: Show the active speaker in a large pane on the left, with additional video thumbnails on the right.
pip: Show the active speaker in a full-screen view, with the first participant inlaid in a corner.
Default: grid
showTextOverlay
boolean
Sets whether a text overlay is displayed. You can configure the contents of the overlay with the text.* properties.
Default: false
showImageOverlay
boolean
Sets whether an image overlay is displayed. You can configure the display of the overlay with the image.* properties. The image used must be passed in the session_id layout option when the stream or recording is started.
Default: false
showBannerOverlay
boolean
Sets whether a banner overlay is displayed. The banner can be used for TV-style "lower third" graphics, or displayed in any corner. You can configure the content of the overlay with the banner.* properties.
Default: false
showWebFrameOverlay
boolean
Sets whether a WebFrame overlay is displayed. You can configure the display of this live web browser overlay with the webFrame.* properties. The URL and the browser viewport size can be changed while your stream or recording is running.
Default: false
showSidebar
boolean
Sets whether a sidebar is displayed. You can configure the display of the sidebar with the sidebar.* properties.
Default: false
showTitleSlate
boolean
Sets whether a title screen (a "slate") is displayed. You can configure the display of the slate with the titleSlate.* properties.
Default: false
enableAutoOpeningSlate
boolean
Sets whether a title screen (a "slate") is automatically shown at the start of the stream. You can configure the display of this automatic slate with the openingSlate. properties.
Default: false
Group: videoSettings

videoSettings.maxCamStreams
number
Limits the number of non-screenshare streams that are included in the output.
Default: 25
videoSettings.preferredParticipantIds
string
Lets you do render-time reordering of video inputs according to participant IDs within a Daily room. To enable this sorting, pass a comma-separated list of participant IDs as the value for this param; video inputs matching these IDs will be moved to the top of the list. If you pass an ID that is not present in the room, it's ignored. All other video inputs will remain in their original order. The default value is an empty string indicating no reordering. Also note that videoSettings.preferScreenshare takes precedence over the ordering passed here. For more information about how participants and videos are sorted, see the section on selecting participants.
Default:
videoSettings.preferScreenshare
boolean
When enabled, screen share inputs will be sorted before camera inputs. This is useful when prioritizing screen shares in your layout, especially when all inputs are not included in the final stream. For more information about how participants and videos are sorted, see the section on selecting participants.
Default: false
videoSettings.omitPausedVideo
boolean
When enabled, paused video inputs will not be included. By default this is off, and paused inputs are displayed with a placeholder graphic. ("Paused video" means that the video track for a participant is not available, either due to user action or network conditions.)
Default: false
videoSettings.omitAudioOnly
boolean
When enabled, audio-only inputs will not be included in rendering. By default this is off, and audio participants are displayed with a placeholder graphic.
Default: false
videoSettings.omitExtraScreenshares
boolean
When enabled, any screenshare video inputs beyond the first one will not be included in rendering. You can control the ordering of the inputs using the layout.participants property to explicitly select which participant should be first in the list of inputs.
Default: false
videoSettings.showParticipantLabels
boolean
Sets whether call participants' names are displayed on their video tiles.
Default: false
videoSettings.roundedCorners
boolean
Sets whether to display video tiles with squared or rounded corners. Note that some modes (dominant and pip) have additional params to control whether the main video has rounded corners or not.
Default: false
videoSettings.cornerRadius_gu
number
Sets the corner radius applied to video layers when videoSettings.roundedCorners is enabled, in grid units.
Default: 1.2
videoSettings.scaleMode
string
Controls how source video is displayed inside a tile if they have different aspect ratios. Use 'fill' to crop the video to fill the entire tile. Use 'fit' to make sure the entire video fits inside the tile, adding letterboxes or pillarboxes as necessary.
Default: fill
videoSettings.scaleModeForScreenshare
string
Controls how a screenshare video is displayed inside a tile if they have different aspect ratios. Use 'fill' to crop the video to fill the entire tile. Use 'fit' to make sure the entire video fits inside the tile, adding letterboxes or pillarboxes as necessary.
Default: fit
videoSettings.placeholder.bgColor
string
Sets the background color for video placeholder tile. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgb(0, 50, 80)
videoSettings.highlight.color
string
Sets the highlight color. It's used as the border color to indicate the 'dominant' video input (typically the active speaker). Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgb(255, 255, 255)
videoSettings.highlight.stroke_gu
number
Sets the stroke width used to render a highlight border. See also 'videoSettings.highlight.color'. Specified in grid units.
Default: 0.2
videoSettings.split.margin_gu
number
Sets the visual margin between the two video layers shown in split mode, in grid units.
Default: 0
videoSettings.split.direction
string
Selects whether the 'split' layout mode is rendered in a horizontal or vertical configuration. The default value 'auto-by-viewport' means that the split direction will be automatically selected to be most appropriate for the current viewport size: if the viewport is landscape or square, the split axis is vertical; if portrait, the split axis is horizontal. Valid options: 'auto-by-viewport', 'vertical', 'horizontal'
Default: auto-by-viewport
videoSettings.split.scaleModeOverrides
string
Overrides the scaleMode setting for the split layout mode. Both sides of the split can have separately defined scale modes. Pass a comma-separated list such as fill, fit (this would set the left-hand side video to fill and the right-hand side video to fit). See documentation for the videoSettings.scaleMode parameter for the valid options. Note that this setting also overrides videoSettings.scaleModeForScreenshare.
Default:
videoSettings.grid.useDominantForSharing
boolean
When enabled, the layout will automatically switch to dominant mode from grid if a screenshare video input is available. By using this automatic behavior, you avoid having to manually switch the mode via an API call.
Default: false
videoSettings.grid.itemInterval_gu
number
Overrides the visual margin between items in grid mode, in grid units. The default value of -1 means that the layout algorithm selects a reasonable margin automatically depending on the number of videos.
Default: -1
videoSettings.grid.outerPadding_gu
number
Overrides the outer padding around items in grid mode, in grid units. The default value of -1 means that the layout algorithm selects a reasonable padding automatically depending on the number of videos.
Default: -1
videoSettings.grid.highlightDominant
boolean
By default, the grid mode will highlight the dominant video (typically the "active speaker") with a light outline. You can disable the highlight using this setting.
Default: true
videoSettings.grid.preserveAspectRatio
boolean
By default, the layout for the grid mode will try to preserve the aspect ratio of the input videos, i.e. avoid cropping the videos and instead add margins around the grid if needed. Setting this parameter to false will make the grid layout fill all available area, potentially cropping the videos.
Default: true
videoSettings.dominant.position
string
Control where the dominant (or "active speaker") video is displayed in the dominant layout mode. Values are left, right, top or bottom.
Default: left
videoSettings.dominant.splitPos
number
Sets the position of the imaginary line separating the dominant video from the smaller tiles when using the dominant layout. Values are from 0 to 1. The default is 0.8, so if videoSettings.dominant.position is set to left, the dominant video will take 80% of the width of the screen on the left.
Default: 0.8
videoSettings.dominant.numChiclets
number
Controls how many "chiclets", or smaller video tiles, appear alongside the dominant video when using the dominant layout.
Default: 5
videoSettings.dominant.followDomFlag
boolean
When in dominant mode, the large tile displays the active speaker by default. Turn off this followDomFlag to display the first participant instead of the active speaker.
Default: true
videoSettings.dominant.itemInterval_gu
number
Margin between the “chiclet” items, in grid units.
Default: 0.7
videoSettings.dominant.outerPadding_gu
number
Padding around the row/column of “chiclet” items, in grid units.
Default: 0.5
videoSettings.dominant.splitMargin_gu
number
Margin between the "dominant" video and the row/column of "chiclet" items, in grid units.
Default: 0
videoSettings.dominant.sharpCornersOnMain
boolean
Sets whether the "dominant" video will be rendered with rounded corners when videoSettings.roundedCorners is enabled. Defaults to false because sharp corners are a more natural choice for the default configuration where the dominant video is tightly aligned to viewport edges.
Default: true
videoSettings.pip.position
string
Sets the position of the smaller video in the pip (picture-in-picture) layout. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'.
Default: top-right
videoSettings.pip.aspectRatio
number
Sets the aspect ratio of the smaller video in the pip layout. The default is 1.0, which produces a square video.
Default: 1
videoSettings.pip.height_gu
number
Sets the height of the smaller video in the pip layout, measured in grid units.
Default: 12
videoSettings.pip.margin_gu
number
Sets the margin between the smaller video and the edge of the frame in the pip layout, in grid units.
Default: 1.5
videoSettings.pip.followDomFlag
boolean
When in "pip" (or picture-in-picture) mode, the overlay tile displays the first participant in the participant array by default. Turn on this followDomFlag to display the active speaker instead.
Default: false
videoSettings.pip.sharpCornersOnMain
boolean
Sets whether the main video in pip mode will be rendered with rounded corners when videoSettings.roundedCorners is enabled. Defaults to false because sharp corners are a more natural choice for the default configuration where the main video is full-screen (no margin to viewport edges).
Default: true
videoSettings.labels.fontFamily
string
Sets the participant label style option: font family. Valid options: DMSans, Roboto, RobotoCondensed, Bitter, Exo, Magra, SuezOne, Teko
Default: Roboto
videoSettings.labels.fontWeight
string
Sets the participant label text font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 600
videoSettings.labels.fontSize_pct
number
Sets the participant label text font size.
Default: 100
videoSettings.labels.offset_x_gu
number
Sets the offset value for participant labels on the x-axis, measured in grid units.
Default: 0
videoSettings.labels.offset_y_gu
number
Sets the offset value for participant labels on the y-axis, measured in grid units.
Default: 0
videoSettings.labels.color
string
Sets the participant label font color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
videoSettings.labels.strokeColor
string
Sets the label font stroke color (the line outlining the text letters). Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.9)
videoSettings.margin.left_gu
number
Sets the left margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.right_gu
number
Sets the right margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.top_gu
number
Sets the top margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.bottom_gu
number
Sets the bottom margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
Group: text

text.content
string
Sets the string to be displayed if showTextOverlay is true.
Default:
text.source
string
Sets the data source used for the text displayed in the overlay. The default value 'param' means that the value of param text.content is used. Valid options: param, highlightLines.items, chatMessages, transcript
Default: param
text.align_horizontal
string
Sets the horizontal alignment of the text overlay within the video frame. Values are left, right, or center.
Default: center
text.align_vertical
string
Sets the vertical alignment of the text overlay within the video frame. Values are top, bottom, or center.
Default: center
text.offset_x_gu
number
Sets an x-offset (horizontal) to be applied to the text overlay's position based on the values of text.align_horizontal and text.align_vertical.
Default: 0
text.offset_y_gu
number
Sets a y-offset (vertical) to be applied to the text overlay's position based on the values of text.align_horizontal and text.align_vertical.
Default: 0
text.rotation_deg
number
Applies a rotation to the text overlay. Units are degrees, and positive is a clockwise rotation.
Default: 0
text.fontFamily
string
Sets the font of the text overlay. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: DMSans
text.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
text.fontStyle
string
Sets the font style for text. Valid options: 'normal','italic'.
Default:
text.fontSize_gu
number
Sets the text overlay font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
text.color
string
Sets the color and transparency of the text overlay. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 250, 200, 0.95)
text.strokeColor
string
Sets the color of the stroke drawn around the characters in the text overlay. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.8)
text.stroke_gu
number
Sets the width of the stroke drawn around the characters in the text overlay. Specified in grid units.
Default: 0.5
text.highlight.color
text
Sets the color and transparency of a highlighted item in the text overlay. To display a highlight, the value of param text.source must be set to highlightLines.items. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 0, 1)
text.highlight.fontWeight
enum
Sets the font weight of a highlighted item in the text overlay. To display a highlight, the value of param text.source must be set to highlightLines.items.
Default: 700
Group: image

image.assetName
string
Sets the overlay image. Icon asset must be included in session_assets object. showImageOverlay must be true.
Default: overlay.png
image.emoji
text
Sets an emoji to be rendered instead of an image asset. If this string is non-empty, it will override the value of image.assetName. The string value must be an emoji.
Default:
image.position
string
Sets position of overlay image. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
Default: top-right
image.fullScreen
boolean
Sets overlay image to full screen.
Default: false
image.aspectRatio
number
Sets aspect ratio of overlay image.
Default: 1.778
image.height_gu
number
Sets height of overlay image, in grid units.
Default: 12
image.margin_gu
number
Sets margin between the overlay image and the viewport edge, in grid units.
Default: 1.5
image.opacity
number
Sets opacity of overlay image, in range 0-1. Default value of 1 is full opacity.
Default: 1
image.enableFade
boolean
Sets the overlay image to fade in or out when the showImageOverlay property is updated.
Default: true
Group: webFrame

webFrame.url
string
Sets the web page URL to be loaded into the WebFrame overlay's embedded browser.
Default:
webFrame.viewportWidth_px
number
Sets the width of the embedded browser window used to render the WebFrame overlay.
Default: 1280
webFrame.viewportHeight_px
number
Sets the height of the embedded browser window used to render the WebFrame overlay.
Default: 720
webFrame.position
string
Sets position of the WebFrame overlay. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
Default: top-right
webFrame.fullScreen
boolean
Sets the WebFrame overlay to full screen.
Default: false
webFrame.height_gu
number
Sets height of the WebFrame overlay, in grid units.
Default: 12
webFrame.margin_gu
number
Sets margin between the WebFrame overlay and the viewport edge, in grid units.
Default: 1.5
webFrame.opacity
number
Sets opacity of the WebFrame overlay, in range 0-1. Default value of 1 is full opacity.
Default: 1
webFrame.enableFade
boolean
Sets the WebFrame overlay to fade in or out when the showWebFrameOverlay property is updated.
Default: true
webFrame.keyPress.keyName
string
Sets the keyboard key to be sent to the WebFrame browser in a simulated key press. Valid options:

Digits 0 - 9
Letters A - Z
ASCII special characters, e.g. !, @, +, >, etc.
Function keys F1 - F12
Enter
Escape
Backspace
Tab
Arrow keys ArrowUp, ArrowDown, ArrowLeft, ArrowRight
PageDown, PageUp
Default: ArrowRight
webFrame.keyPress.modifiers
string
Sets keyboard modifier keys to be sent to the WebFrame browser in a simulated key press. Valid options: "Shift", "Control", "Alt", "Meta" (on a Mac keyboard, Alt is equal to Option and Meta is equal to Command).
Default:
webFrame.keyPress.key
number
Triggers a simulated key press to be sent to WebFrame. To send a key press, increment the value of key. (Note the difference between this and keyName which is the simulated key to be sent.)
Default: 0
Group: banner

banner.title
text
Sets the title text displayed in the banner component.
Default: Hello world
banner.subtitle
text
Sets the subtitle text displayed in the banner component.
Default: This is an example subtitle
banner.source
string
Sets the data source for the text displayed in the banner component. Valid options: param, highlightLines.items, chatMessages, transcript
Default: param
banner.position
string
Sets position of the banner component. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
banner.enableTransition
boolean
Sets the banner to fade in or out when the showBannerOverlay property is updated.
Default: true
banner.margin_x_gu
number
Horizontal margin, specified in grid units.
Default: 0
banner.margin_y_gu
number
Vertical margin, specified in grid units.
Default: 1
banner.padding_gu
number
Padding inside the component, specified in grid units.
Default: 2
banner.alwaysUseMaxW
boolean
Sets whether the banner component will always use its maximum width (specified using banner.maxW_pct_default and banner.maxW_pct_portrait). If false, the banner component will shrink horizontally to fit text inside it, if appropriate.
Default: false
banner.maxW_pct_default
number
Sets the maximum width for the banner component, as a percentage of the viewport size.
Default: 65
banner.maxW_pct_portrait
number
Sets the maximum width for the banner component, as a percentage of the viewport size, applied only when the viewport aspect ratio is portrait (i.e. smaller than 1). This override is useful because on a narrow screen the banner display typically needs more horizontal space than on a landscape screen.
Default: 90
banner.rotation_deg
number
Applies a rotation to the banner component. Units are degrees, and positive is a clockwise rotation.
Default: 0
banner.cornerRadius_gu
number
Sets the corner radius of the banner component outline. Specified in grid units.
Default: 0
banner.showIcon
boolean
Sets whether an icon is displayed in the banner component (true or false).
Default: true
banner.icon.assetName
text
Sets image asset value for the banner icon. Icon asset must be included in session_assets object.
Default:
banner.icon.emoji
text
Sets an emoji to be rendered as the banner icon. If this string is non-empty, it will override banner.icon.assetName. The string value must be an emoji.
Default: 🎉
banner.icon.size_gu
number
Sets the size of the banner icon, specified in grid units.
Default: 3
banner.color
text
Sets the banner component's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(50, 60, 200, 0.9)
banner.strokeColor
text
Sets the color of the outline drawn around the banner component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 30, 0.44)
banner.stroke_gu
number
Sets the width of the stroke drawn around the banner component. Specified in grid units.
Default: 0
banner.text.color
text
Sets the banner component's text color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
banner.text.strokeColor
text
Sets the color of the stroke drawn around the characters in the banner component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.1)
banner.text.stroke_gu
number
Sets the width of the stroke drawn around the characters in the banner component. Specified in grid units.
Default: 0.5
banner.text.fontFamily
string
Sets the font of text displayed in the banner component. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Roboto
banner.title.fontSize_gu
number
Sets the banner title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2
banner.title.fontWeight
string
Sets the banner title font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
banner.title.fontStyle
string
Sets the font style for the banner title. Valid options: 'normal','italic'.
Default:
banner.subtitle.fontSize_gu
number
Sets the banner subtitle font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 1.5
banner.subtitle.fontWeight
string
Sets the banner subtitle font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 300
banner.subtitle.fontStyle
string
Sets the font style for the banner subtitle. Valid options: 'normal','italic'.
Default:
Group: toast

toast.key
number
Triggers display of toast component. To send a toast, increment the value of key
Default: 0
toast.text
string
Sets text displayed in toast component.
Default: Hello world
toast.source
string
Sets the data source used for the text displayed in the toast component. The default value param means that the value of param toast.content is used. Valid options: param, chatMessages, transcript
Default: param
toast.duration_secs
number
Sets duration of time toast component is displayed (in seconds).
Default: 4
toast.maxW_pct_default
number
Sets the maximum width for the toast component, as a percentage of the viewport size.
Default: 50
toast.maxW_pct_portrait
number
Sets the maximum width for the toast component, as a percentage of the viewport size, applied only when the viewport aspect ratio is portrait (i.e. smaller than 1). This override is useful because on a narrow screen the toast display typically needs more horizontal space than on a landscape screen.
Default: 80
toast.showIcon
boolean
Sets whether icon is displayed in toast component (true or false).
Default: true
toast.icon.assetName
string
Sets asset value for toast icon. Icon asset must be included in session_assets object.
Default:
toast.icon.emoji
text
Sets an emoji to be rendered as the toast icon. If this string is non-empty, it will override toast.icon.assetName. The string value must be an emoji.
Default: 🎉
toast.icon.size_gu
number
Sets the size of the toast icon, in grid units.
Default: 3
toast.color
string
Sets the toast component's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(15, 50, 110, 0.6)
toast.strokeColor
string
Sets the color of the stroke drawn around the text characters in the toast component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 30, 0.44)
toast.text.color
string
Sets the toast component's text color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
toast.text.fontFamily
string
Sets the toast component's font family. Valid options: DMSans, Roboto, RobotoCondensed, Bitter, Exo, Magra, SuezOne, Teko
Default: Roboto
toast.text.fontWeight
number
Sets the font weight for the toast component's text. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
toast.text.fontSize_pct
number
Sets the font size for the toast component's text.
Default: 100
Group: openingSlate

openingSlate.duration_secs
number
Sets the number of seconds that the opening slate will be displayed when the stream starts. After this time, the slate goes away with a fade-out effect.
Default: 4
openingSlate.title
string
Sets text displayed in the main title of the opening slate.
Default: Welcome
openingSlate.subtitle
string
Sets text displayed in the subtitle (second line) of the opening slate.
Default:
openingSlate.bgImageAssetName
string
Sets an image to be used as the background for the slate. This image asset must be included in session_assets object when starting the stream/recording.
Default:
openingSlate.bgColor
string
Sets the slate's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 1)
openingSlate.textColor
string
Sets the text color of the titles in the slate. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 1)
openingSlate.fontFamily
string
Sets the font of the titles in the slate. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Bitter
openingSlate.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
openingSlate.fontStyle
string
Sets the font style for the titles in the slate. Valid options: 'normal','italic'.
Default:
openingSlate.fontSize_gu
number
Sets the main title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
openingSlate.subtitle.fontSize_pct
number
Sets the subtitle font size as a percentage of the main title.
Default: 75
openingSlate.subtitle.fontWeight
string
Selects a weight variant from the selected font family specifically for the subtitle. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 400
Group: titleSlate

titleSlate.enableTransition
boolean
Sets the slate to fade in or out when the showTitleSlate property is updated.'
Default: true
titleSlate.title
string
Sets text displayed in the main title of the slate.
Default: Title slate
titleSlate.subtitle
string
Sets text displayed in the subtitle (second line) of the slate.
Default: Subtitle
titleSlate.bgImageAssetName
string
Sets an image to be used as the background for the slate. This image asset must be included in session_assets object when starting the stream/recording.
Default:
titleSlate.bgColor
string
Sets the slate's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 1)
titleSlate.textColor
string
Sets the text color of the titles in the slate. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 1)
titleSlate.fontFamily
string
Sets the font of the titles in the slate. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Bitter
titleSlate.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
titleSlate.fontStyle
string
Sets the font style for the titles in the slate. Valid options: 'normal','italic'.
Default:
titleSlate.fontSize_gu
number
Sets the main title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
titleSlate.subtitle.fontSize_pct
number
Sets the subtitle font size as a percentage of the main title.
Default: 75
titleSlate.subtitle.fontWeight
string
Selects a weight variant from the selected font family specifically for the subtitle. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 400
Group: sidebar

sidebar.shrinkVideoLayout
boolean
Sets whether the sidebar is displayed on top of video elements. If set to true , the video layout is shrunk horizontally to make room for the sidebar so they don't overlap.
Default: false
sidebar.source
string
Sets the data source for the text displayed in the sidebar. Valid options: param, highlightLines.items, chatMessages, transcript
Default: highlightLines.items
sidebar.padding_gu
number
Padding inside the sidebar, specified in grid units.
Default: 1.5
sidebar.width_pct_landscape
number
Sets the width of the sidebar, as a percentage of the viewport size, applied when the viewport is landscape (its aspect ratio is greater than 1).
Default: 30
sidebar.height_pct_portrait
number
Sets the width of the sidebar, as a percentage of the viewport size, applied when the viewport is portrait or square (its aspect ratio is less than or equal to 1).
Default: 25
sidebar.bgColor
text
Sets the sidebar's background color and opacity. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 50, 0.55)
sidebar.textColor
text
Sets the sidebar's text color and opacity. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 0.94)
sidebar.fontFamily
string
Sets the font of text displayed in the sidebar. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: DMSans
sidebar.fontWeight
string
Sets the sidebar text font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 300
sidebar.fontStyle
string
Sets the font style for text in the sidebar. Valid options: 'normal','italic'.
Default:
sidebar.fontSize_gu
number
Sets the sidebar text font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 1.4
sidebar.textHighlight.color
text
Sets the color used for the highlighted item in the sidebar.
Default: rgba(255, 230, 0, 1)
sidebar.textHighlight.fontWeight
string
Sets the font weight used for the highlighted item in the sidebar.
Default: 600
Group: highlightLines

highlightLines.items
text
Sets a list of text items. Items must be separated by newline characters. This param is a data source that can be displayed in other components like TextOverlay, Banner and Sidebar using the various "source" params available in the settings for those components.
highlightLines.position
number
Sets the highlight index associated with the text items specified in highlightLines.items. The item at this index will be displayed using a special highlight style (which depends on the component used to display this data). If you don't want a highlight, set this value to -1.
Default: 0
Group: emojiReactions

emojiReactions.source
string
Sets the data source used for emoji reactions. The default value emojiReactions means that this component will display emojis that are sent via the standard source API.

The other valid option is param, which lets you send a reaction using param values instead of the standard source. The steps are as follows: set emojiReactions.source to param, set a single-emoji string for emojiReactions.emoji, and increment the value of emojiReactions.key to send one emoji for display.
Default: emojiReactions
emojiReactions.key
number
If emojiReactions.source is set to param, increment this numeric key to send a new emoji for display.
Default: 0
emojiReactions.emoji
text
If emojiReactions.source is set to param, set a single emoji as the string value for this param, and it will be the next emoji reaction rendered when emojiReactions.key is incremented.
Default:
emojiReactions.offset_x_gu
number
Sets a horizontal offset applied to the emoji reactions animation rendering (each new emoji floats up from the bottom of the screen). Specified in grid units.
Default: 0
Group: debug

debug.showRoomState
boolean
When set to true, a room state debugging display is visible. It prints various information about participant state.
Default: false
debug.overlayOpacity
number
Sets the opacity of the debugging display which can be toggled using debug.showRoomState.
Default: 90
Selecting participants

The baseline composition has several modes that display multiple participant videos. You may be wondering how to control which participants appear in specific places within those layouts.

Internally, VCS uses an ordered array of video inputs that it calls "video input slots". By default, that array will contain all participants in the order in which they joined the call. But there are two ways you can override this default behavior and choose which participants appear in your layout:

Participant selection on the room level using the participants property.
Input reordering on the composition level (a.k.a. switching) using the preferredParticipantIds and preferScreenshare params available in the baseline composition.
These two are not mutually exclusive. What's the difference, and when should you use one or the other?

Room-level participant selection is a powerful generic tool. It lets you choose any participants within the room, and will trigger any necessary backend connections so that a participant's audio and video streams become available to the VCS rendering server. This means there may be a slight delay as connections are made.

In contrast, composition-level input reordering (a.k.a. switching) happens at the very last moment in the VCS engine just before a video frame is rendered. (The name "switching" refers to a video switcher, a hardware device used in traditional video production for this kind of input control.) It's applied together with any other composition param updates you're sending, so there is a guarantee of synchronization. You should use this method when you want to ensure that the reordering of inputs happens precisely at the same time as your update to some other composition param value(s). For example, if you're switching a layout mode and want the inputs to be sorted in a different way simultaneously.

You can use the two methods together. Room-level selection using the participants property lets you establish the participants whose streams will be available to the rendering. You can then do rapid switching within that selection using the preferredParticipantIds and preferScreenshare params in the baseline composition.

Here's an example of selecting three specific participant video tracks, everyone's audio tracks, and sorting the video by most recent active speaker:

JavaScript
Copy to clipboard
{
    layout: {
        preset: "custom",
        composition_params: {...},
        participants: {
            video: ["participant-guid-1", "participant-guid-2", "participant-guid-3"],
            audio: ["*"],
            sort: "active"
        }
    }
}

Here's another example where we're further sorting the same video tracks using the baseline composition params. The params update is switching to a different layout mode ('split'). This mode can only show two participants, so we use videoSettings.preferredParticipantIds to select the two participants in a clean frame-synchronized way, without having to modify the underlying connections made via the participants property:

JavaScript
Copy to clipboard
{
    layout: {
        preset: "custom",
        composition_params: {
            mode: 'split',
            'videoSettings.preferredParticipantIds': 'participant-guid-2, participant-guid-1',
        },
        participants: {
            video: ["participant-guid-1", "participant-guid-2", "participant-guid-3"],
            audio: ["*"],
            sort: "active"
        }
    }
}

If you include the participants object in a startLiveStreaming()/startRecording() or updateLiveStreaming()/updateRecording() call, you need to include it in any subsequent updateLiveStreaming()/updateRecording() calls as well, even if you aren't changing it.
If you set the participants property for your recording or live stream and then make an updateLiveStreaming()/updateRecording() call to update the composition_params, you'll need to resend the same values you used before in the participants property. This is true even if you are not updating the participants property. If you don't, the participant configuration will reset to default, as if you hadn't set it in the first place —meaning VCS will receive all audio and video tracks from all participants, sorted by the order in which the participants joined the call.
participants properties

video
array
Required. An array of strings indicating which participant videos to make available to VCS. Possible values are:

["participant-guid-1", "participant-guid-2", "participant-guid-3"]: A list of specific participant IDs
["*"]: everyone
["owners"]: All call owners
audio
array
An optional array of strings indicating which participant audio tracks to make available to VCS. Possible values are the same as the video property.
sort
string
The only currently valid value for this property is "active". This property controls the order in which VCS sees the participant video tracks. When set to "active", each time the call's active speaker changes to a different participant, that participant will bubble up to the first position in the array. In other words, setting sort to "active" will cause an n-tile layout to always show the n most recent speakers in the call. If you leave the property unset, the list of participants will stay in a fixed order: either the order you specified in the video property, or in the order they joined the call if you use "*" or "owners".
Session assets

Session assets — images or custom VCS components — that can be passed as assets and used during a live stream or cloud recording. To learn more, visit our Session assets page in the VCS SDK reference docs.

Note: Session assets must be made available at the beginning of the recording or live stream even if they are not used until later in the call.

Example requests


Default

Single Participant

Active Participant

Portrait

Custom

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"layout": {"preset": "default", "max_cam_streams": 1}}' \
     https://api.daily.co/v1/rooms/hello/recordings/start
            
POST
/rooms/:name/recordings/update
PAY-AS-YOU-GO

Update a recording with a given layout configuration.

You can pass configuration properties to this endpoint to control the look and feel of the recording.

"raw-tracks" recordings can not be updated, and will return a 400 error.

The options currently include:

height, width: Can be specified to control the resolution of the live stream. The value must be even, i.e., a multiple of 2.
backgroundColor: Specifies the background color of the stream, formatted as #rrggbb or #aarrggbb string.
fps: Specifies the video frame rate per second.
videoBitrate: Specifies the video bitrate in kilobits per second (kbps) to use for video output. Value can range between 10 and 10000. If not specified, the following bitrate values will be used for each given resolution:

1080p: 5000
720p: 3000
480p: 2000
360p: 1000
audioBitrate: Specifies the audio bitrate in kilobits per second (kbps) to use for audio output. Value can range between 10 and 320.
minIdleTimeOut: Amount of time in seconds to wait before ending a recording or live stream when the room is idle (e.g. when all users have muted video and audio). Default: 300 (seconds). Note: Once the timeout has been reached, it typically takes an additional 1-3 minutes for the recording or live stream to be shut down.
maxDuration: maximum duration in seconds after which recording/streaming is forcefully stopped. Defaults: 10800 seconds (3 hours) for recordings, 86400 seconds (24 hours) for streaming. This is a preventive circuit breaker to prevent billing surprises in case a user starts recording/streaming and leaves the room.
instanceId: UUID for a streaming or recording session. Used when multiple streaming or recording sessions are running for single room. Default: "c3df927c-f738-4471-a2b7-066fa7e95a6b". Note: "c3df927c-f738-4471-a2b7-066fa7e95a6b" is reserved internally; do not use this UUID.
type: specify type of recording ("cloud", "raw-tracks", "local") to start. Particular recording type must be enabled for the room or domain with enable_recording property.
layout: an object specifying the way participants’ videos are laid out in the live stream. A preset key with one of the following values must be provided:

'default': This is the default grid layout, which renders participants in a grid, or in a vertical grid to the right, if a screen share is enabled. Optionally, a max_cam_streams integer key can be provided to specify how many cameras to include in the grid. The default value is 20, which is also the maximum number of cameras in a grid. The maximum may be increased at a later date.
'audio-only': This layout creates an audio only cloud recording. Video will not be a part of the recording.
'single-participant': Use this layout to limit the audio and video to be streamed to a specific participant. The selected participant’s session ID must be specified via a session_id key.
'active-participant': This layout focuses on the current speaker, and places up to 9 other cameras to the right in a vertical grid in the order in which they last spoke.
'portrait': Allows for mobile-friendly layouts. The video will be forced into portrait mode, where up to 2 participants will be shown. An additional variant key may be specified. Valid values are:
'vertical' for a vertical grid layout (the default)
'inset'for having one participant's video take up the entire screen, and the other inset in a smaller rectangle. Participants' videos are scaled and cropped to fit the entire available space. Participants with the is_owner flag are shown lower in the grid (vertical variant), or full screen (inset variant).
'raw-tracks-audio-only': record only the audio tracks for raw-tracks recording. (NOTE: applicable only for raw-tracks recording)

'custom': Allows for custom layouts. (See below.)
Path params

name
string
The name of the room.
Body params

width
number
Property that specifies the output width of the given stream.
height
number
Property that specifies the output height of the given stream.
fps
number
Property that specifies the video frame rate per second.
videoBitrate
number
Property that specifies the video bitrate for the output video in kilobits per second (kbps).
audioBitrate
number
Property that specifies the audio bitrate for the output audio in kilobits per second (kbps).
minIdleTimeOut
number
Amount of time in seconds to wait before ending a recording or live stream when the room is idle (e.g. when all users have muted video and audio). Default: 300 (seconds). Note: Once the timeout has been reached, it typically takes an additional 1-3 minutes for the recording or live stream to be shut down.
maxDuration
number
Maximum duration in seconds after which recording/streaming is forcefully stopped. Default: `15000` seconds (3 hours). This is a preventive circuit breaker to prevent billing surprises in case a user starts recording/streaming and leaves the room.
backgroundColor
string
Specifies the background color of the stream, formatted as #rrggbb or #aarrggbb string.
instanceId
string
UUID for a streaming or recording session. Used when multiple streaming or recording sessions are running for single room.
type
string
specify type of recording (cloud, raw-tracks, local) to start. Particular recording type must be enabled for the room or domain with enable_recording property.
layout
object
An object specifying the way participants’ videos are laid out in the live stream. See given layout configs for description of fields. Preset must be defined.
Default Layout

preset
string
Options: "default"
max_cam_streams
number
Single Participant Layout

preset
string
Options: "single-participant"
session_id
string
Active Participant Layout

preset
string
Options: "active-participant"
Portrait Layout

preset
string
Options: "portrait"
variant
string
Options: "vertical","inset"
max_cam_streams
number
Custom Layout

preset
string
Options: "custom"
composition_id
string
composition_params
object
session_assets
object
Custom video layouts with VCS baseline composition

The baseline composition option is only available for cloud recordings and live streaming.
Daily offers a "baseline" composition option via the "custom" layout preset for customizing your video layouts while recording. This option allows for even more flexibility while using Daily's recording API.

Review our Video Component System (VCS) guide or VCS Simulator for additional information and code examples.
Many VCS properties use a "grid unit". The grid unit is a designer-friendly, device-independent unit. The default grid size is 1/36 of the output's minimum dimension. In other words, 1gu = 20px on a 720p stream and 30px on a 1080p stream. Learn more about grid units in our [VCS SDK docs](/reference/vcs/layout-api#the-grid-unit).

composition_params

mode
string
Sets the layout mode. Valid options:

single: Show a single full-screen video.
split: Show the first two participants side-by-side.
grid: Show up to 20 videos in a grid layout.
dominant: Show the active speaker in a large pane on the left, with additional video thumbnails on the right.
pip: Show the active speaker in a full-screen view, with the first participant inlaid in a corner.
Default: grid
showTextOverlay
boolean
Sets whether a text overlay is displayed. You can configure the contents of the overlay with the text.* properties.
Default: false
showImageOverlay
boolean
Sets whether an image overlay is displayed. You can configure the display of the overlay with the image.* properties. The image used must be passed in the session_id layout option when the stream or recording is started.
Default: false
showBannerOverlay
boolean
Sets whether a banner overlay is displayed. The banner can be used for TV-style "lower third" graphics, or displayed in any corner. You can configure the content of the overlay with the banner.* properties.
Default: false
showWebFrameOverlay
boolean
Sets whether a WebFrame overlay is displayed. You can configure the display of this live web browser overlay with the webFrame.* properties. The URL and the browser viewport size can be changed while your stream or recording is running.
Default: false
showSidebar
boolean
Sets whether a sidebar is displayed. You can configure the display of the sidebar with the sidebar.* properties.
Default: false
showTitleSlate
boolean
Sets whether a title screen (a "slate") is displayed. You can configure the display of the slate with the titleSlate.* properties.
Default: false
enableAutoOpeningSlate
boolean
Sets whether a title screen (a "slate") is automatically shown at the start of the stream. You can configure the display of this automatic slate with the openingSlate. properties.
Default: false
Group: videoSettings

videoSettings.maxCamStreams
number
Limits the number of non-screenshare streams that are included in the output.
Default: 25
videoSettings.preferredParticipantIds
string
Lets you do render-time reordering of video inputs according to participant IDs within a Daily room. To enable this sorting, pass a comma-separated list of participant IDs as the value for this param; video inputs matching these IDs will be moved to the top of the list. If you pass an ID that is not present in the room, it's ignored. All other video inputs will remain in their original order. The default value is an empty string indicating no reordering. Also note that videoSettings.preferScreenshare takes precedence over the ordering passed here. For more information about how participants and videos are sorted, see the section on selecting participants.
Default:
videoSettings.preferScreenshare
boolean
When enabled, screen share inputs will be sorted before camera inputs. This is useful when prioritizing screen shares in your layout, especially when all inputs are not included in the final stream. For more information about how participants and videos are sorted, see the section on selecting participants.
Default: false
videoSettings.omitPausedVideo
boolean
When enabled, paused video inputs will not be included. By default this is off, and paused inputs are displayed with a placeholder graphic. ("Paused video" means that the video track for a participant is not available, either due to user action or network conditions.)
Default: false
videoSettings.omitAudioOnly
boolean
When enabled, audio-only inputs will not be included in rendering. By default this is off, and audio participants are displayed with a placeholder graphic.
Default: false
videoSettings.omitExtraScreenshares
boolean
When enabled, any screenshare video inputs beyond the first one will not be included in rendering. You can control the ordering of the inputs using the layout.participants property to explicitly select which participant should be first in the list of inputs.
Default: false
videoSettings.showParticipantLabels
boolean
Sets whether call participants' names are displayed on their video tiles.
Default: false
videoSettings.roundedCorners
boolean
Sets whether to display video tiles with squared or rounded corners. Note that some modes (dominant and pip) have additional params to control whether the main video has rounded corners or not.
Default: false
videoSettings.cornerRadius_gu
number
Sets the corner radius applied to video layers when videoSettings.roundedCorners is enabled, in grid units.
Default: 1.2
videoSettings.scaleMode
string
Controls how source video is displayed inside a tile if they have different aspect ratios. Use 'fill' to crop the video to fill the entire tile. Use 'fit' to make sure the entire video fits inside the tile, adding letterboxes or pillarboxes as necessary.
Default: fill
videoSettings.scaleModeForScreenshare
string
Controls how a screenshare video is displayed inside a tile if they have different aspect ratios. Use 'fill' to crop the video to fill the entire tile. Use 'fit' to make sure the entire video fits inside the tile, adding letterboxes or pillarboxes as necessary.
Default: fit
videoSettings.placeholder.bgColor
string
Sets the background color for video placeholder tile. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgb(0, 50, 80)
videoSettings.highlight.color
string
Sets the highlight color. It's used as the border color to indicate the 'dominant' video input (typically the active speaker). Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgb(255, 255, 255)
videoSettings.highlight.stroke_gu
number
Sets the stroke width used to render a highlight border. See also 'videoSettings.highlight.color'. Specified in grid units.
Default: 0.2
videoSettings.split.margin_gu
number
Sets the visual margin between the two video layers shown in split mode, in grid units.
Default: 0
videoSettings.split.direction
string
Selects whether the 'split' layout mode is rendered in a horizontal or vertical configuration. The default value 'auto-by-viewport' means that the split direction will be automatically selected to be most appropriate for the current viewport size: if the viewport is landscape or square, the split axis is vertical; if portrait, the split axis is horizontal. Valid options: 'auto-by-viewport', 'vertical', 'horizontal'
Default: auto-by-viewport
videoSettings.split.scaleModeOverrides
string
Overrides the scaleMode setting for the split layout mode. Both sides of the split can have separately defined scale modes. Pass a comma-separated list such as fill, fit (this would set the left-hand side video to fill and the right-hand side video to fit). See documentation for the videoSettings.scaleMode parameter for the valid options. Note that this setting also overrides videoSettings.scaleModeForScreenshare.
Default:
videoSettings.grid.useDominantForSharing
boolean
When enabled, the layout will automatically switch to dominant mode from grid if a screenshare video input is available. By using this automatic behavior, you avoid having to manually switch the mode via an API call.
Default: false
videoSettings.grid.itemInterval_gu
number
Overrides the visual margin between items in grid mode, in grid units. The default value of -1 means that the layout algorithm selects a reasonable margin automatically depending on the number of videos.
Default: -1
videoSettings.grid.outerPadding_gu
number
Overrides the outer padding around items in grid mode, in grid units. The default value of -1 means that the layout algorithm selects a reasonable padding automatically depending on the number of videos.
Default: -1
videoSettings.grid.highlightDominant
boolean
By default, the grid mode will highlight the dominant video (typically the "active speaker") with a light outline. You can disable the highlight using this setting.
Default: true
videoSettings.grid.preserveAspectRatio
boolean
By default, the layout for the grid mode will try to preserve the aspect ratio of the input videos, i.e. avoid cropping the videos and instead add margins around the grid if needed. Setting this parameter to false will make the grid layout fill all available area, potentially cropping the videos.
Default: true
videoSettings.dominant.position
string
Control where the dominant (or "active speaker") video is displayed in the dominant layout mode. Values are left, right, top or bottom.
Default: left
videoSettings.dominant.splitPos
number
Sets the position of the imaginary line separating the dominant video from the smaller tiles when using the dominant layout. Values are from 0 to 1. The default is 0.8, so if videoSettings.dominant.position is set to left, the dominant video will take 80% of the width of the screen on the left.
Default: 0.8
videoSettings.dominant.numChiclets
number
Controls how many "chiclets", or smaller video tiles, appear alongside the dominant video when using the dominant layout.
Default: 5
videoSettings.dominant.followDomFlag
boolean
When in dominant mode, the large tile displays the active speaker by default. Turn off this followDomFlag to display the first participant instead of the active speaker.
Default: true
videoSettings.dominant.itemInterval_gu
number
Margin between the “chiclet” items, in grid units.
Default: 0.7
videoSettings.dominant.outerPadding_gu
number
Padding around the row/column of “chiclet” items, in grid units.
Default: 0.5
videoSettings.dominant.splitMargin_gu
number
Margin between the "dominant" video and the row/column of "chiclet" items, in grid units.
Default: 0
videoSettings.dominant.sharpCornersOnMain
boolean
Sets whether the "dominant" video will be rendered with rounded corners when videoSettings.roundedCorners is enabled. Defaults to false because sharp corners are a more natural choice for the default configuration where the dominant video is tightly aligned to viewport edges.
Default: true
videoSettings.pip.position
string
Sets the position of the smaller video in the pip (picture-in-picture) layout. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'.
Default: top-right
videoSettings.pip.aspectRatio
number
Sets the aspect ratio of the smaller video in the pip layout. The default is 1.0, which produces a square video.
Default: 1
videoSettings.pip.height_gu
number
Sets the height of the smaller video in the pip layout, measured in grid units.
Default: 12
videoSettings.pip.margin_gu
number
Sets the margin between the smaller video and the edge of the frame in the pip layout, in grid units.
Default: 1.5
videoSettings.pip.followDomFlag
boolean
When in "pip" (or picture-in-picture) mode, the overlay tile displays the first participant in the participant array by default. Turn on this followDomFlag to display the active speaker instead.
Default: false
videoSettings.pip.sharpCornersOnMain
boolean
Sets whether the main video in pip mode will be rendered with rounded corners when videoSettings.roundedCorners is enabled. Defaults to false because sharp corners are a more natural choice for the default configuration where the main video is full-screen (no margin to viewport edges).
Default: true
videoSettings.labels.fontFamily
string
Sets the participant label style option: font family. Valid options: DMSans, Roboto, RobotoCondensed, Bitter, Exo, Magra, SuezOne, Teko
Default: Roboto
videoSettings.labels.fontWeight
string
Sets the participant label text font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 600
videoSettings.labels.fontSize_pct
number
Sets the participant label text font size.
Default: 100
videoSettings.labels.offset_x_gu
number
Sets the offset value for participant labels on the x-axis, measured in grid units.
Default: 0
videoSettings.labels.offset_y_gu
number
Sets the offset value for participant labels on the y-axis, measured in grid units.
Default: 0
videoSettings.labels.color
string
Sets the participant label font color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
videoSettings.labels.strokeColor
string
Sets the label font stroke color (the line outlining the text letters). Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.9)
videoSettings.margin.left_gu
number
Sets the left margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.right_gu
number
Sets the right margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.top_gu
number
Sets the top margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.bottom_gu
number
Sets the bottom margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
Group: text

text.content
string
Sets the string to be displayed if showTextOverlay is true.
Default:
text.source
string
Sets the data source used for the text displayed in the overlay. The default value 'param' means that the value of param text.content is used. Valid options: param, highlightLines.items, chatMessages, transcript
Default: param
text.align_horizontal
string
Sets the horizontal alignment of the text overlay within the video frame. Values are left, right, or center.
Default: center
text.align_vertical
string
Sets the vertical alignment of the text overlay within the video frame. Values are top, bottom, or center.
Default: center
text.offset_x_gu
number
Sets an x-offset (horizontal) to be applied to the text overlay's position based on the values of text.align_horizontal and text.align_vertical.
Default: 0
text.offset_y_gu
number
Sets a y-offset (vertical) to be applied to the text overlay's position based on the values of text.align_horizontal and text.align_vertical.
Default: 0
text.rotation_deg
number
Applies a rotation to the text overlay. Units are degrees, and positive is a clockwise rotation.
Default: 0
text.fontFamily
string
Sets the font of the text overlay. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: DMSans
text.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
text.fontStyle
string
Sets the font style for text. Valid options: 'normal','italic'.
Default:
text.fontSize_gu
number
Sets the text overlay font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
text.color
string
Sets the color and transparency of the text overlay. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 250, 200, 0.95)
text.strokeColor
string
Sets the color of the stroke drawn around the characters in the text overlay. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.8)
text.stroke_gu
number
Sets the width of the stroke drawn around the characters in the text overlay. Specified in grid units.
Default: 0.5
text.highlight.color
text
Sets the color and transparency of a highlighted item in the text overlay. To display a highlight, the value of param text.source must be set to highlightLines.items. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 0, 1)
text.highlight.fontWeight
enum
Sets the font weight of a highlighted item in the text overlay. To display a highlight, the value of param text.source must be set to highlightLines.items.
Default: 700
Group: image

image.assetName
string
Sets the overlay image. Icon asset must be included in session_assets object. showImageOverlay must be true.
Default: overlay.png
image.emoji
text
Sets an emoji to be rendered instead of an image asset. If this string is non-empty, it will override the value of image.assetName. The string value must be an emoji.
Default:
image.position
string
Sets position of overlay image. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
Default: top-right
image.fullScreen
boolean
Sets overlay image to full screen.
Default: false
image.aspectRatio
number
Sets aspect ratio of overlay image.
Default: 1.778
image.height_gu
number
Sets height of overlay image, in grid units.
Default: 12
image.margin_gu
number
Sets margin between the overlay image and the viewport edge, in grid units.
Default: 1.5
image.opacity
number
Sets opacity of overlay image, in range 0-1. Default value of 1 is full opacity.
Default: 1
image.enableFade
boolean
Sets the overlay image to fade in or out when the showImageOverlay property is updated.
Default: true
Group: webFrame

webFrame.url
string
Sets the web page URL to be loaded into the WebFrame overlay's embedded browser.
Default:
webFrame.viewportWidth_px
number
Sets the width of the embedded browser window used to render the WebFrame overlay.
Default: 1280
webFrame.viewportHeight_px
number
Sets the height of the embedded browser window used to render the WebFrame overlay.
Default: 720
webFrame.position
string
Sets position of the WebFrame overlay. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
Default: top-right
webFrame.fullScreen
boolean
Sets the WebFrame overlay to full screen.
Default: false
webFrame.height_gu
number
Sets height of the WebFrame overlay, in grid units.
Default: 12
webFrame.margin_gu
number
Sets margin between the WebFrame overlay and the viewport edge, in grid units.
Default: 1.5
webFrame.opacity
number
Sets opacity of the WebFrame overlay, in range 0-1. Default value of 1 is full opacity.
Default: 1
webFrame.enableFade
boolean
Sets the WebFrame overlay to fade in or out when the showWebFrameOverlay property is updated.
Default: true
webFrame.keyPress.keyName
string
Sets the keyboard key to be sent to the WebFrame browser in a simulated key press. Valid options:

Digits 0 - 9
Letters A - Z
ASCII special characters, e.g. !, @, +, >, etc.
Function keys F1 - F12
Enter
Escape
Backspace
Tab
Arrow keys ArrowUp, ArrowDown, ArrowLeft, ArrowRight
PageDown, PageUp
Default: ArrowRight
webFrame.keyPress.modifiers
string
Sets keyboard modifier keys to be sent to the WebFrame browser in a simulated key press. Valid options: "Shift", "Control", "Alt", "Meta" (on a Mac keyboard, Alt is equal to Option and Meta is equal to Command).
Default:
webFrame.keyPress.key
number
Triggers a simulated key press to be sent to WebFrame. To send a key press, increment the value of key. (Note the difference between this and keyName which is the simulated key to be sent.)
Default: 0
Group: banner

banner.title
text
Sets the title text displayed in the banner component.
Default: Hello world
banner.subtitle
text
Sets the subtitle text displayed in the banner component.
Default: This is an example subtitle
banner.source
string
Sets the data source for the text displayed in the banner component. Valid options: param, highlightLines.items, chatMessages, transcript
Default: param
banner.position
string
Sets position of the banner component. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
banner.enableTransition
boolean
Sets the banner to fade in or out when the showBannerOverlay property is updated.
Default: true
banner.margin_x_gu
number
Horizontal margin, specified in grid units.
Default: 0
banner.margin_y_gu
number
Vertical margin, specified in grid units.
Default: 1
banner.padding_gu
number
Padding inside the component, specified in grid units.
Default: 2
banner.alwaysUseMaxW
boolean
Sets whether the banner component will always use its maximum width (specified using banner.maxW_pct_default and banner.maxW_pct_portrait). If false, the banner component will shrink horizontally to fit text inside it, if appropriate.
Default: false
banner.maxW_pct_default
number
Sets the maximum width for the banner component, as a percentage of the viewport size.
Default: 65
banner.maxW_pct_portrait
number
Sets the maximum width for the banner component, as a percentage of the viewport size, applied only when the viewport aspect ratio is portrait (i.e. smaller than 1). This override is useful because on a narrow screen the banner display typically needs more horizontal space than on a landscape screen.
Default: 90
banner.rotation_deg
number
Applies a rotation to the banner component. Units are degrees, and positive is a clockwise rotation.
Default: 0
banner.cornerRadius_gu
number
Sets the corner radius of the banner component outline. Specified in grid units.
Default: 0
banner.showIcon
boolean
Sets whether an icon is displayed in the banner component (true or false).
Default: true
banner.icon.assetName
text
Sets image asset value for the banner icon. Icon asset must be included in session_assets object.
Default:
banner.icon.emoji
text
Sets an emoji to be rendered as the banner icon. If this string is non-empty, it will override banner.icon.assetName. The string value must be an emoji.
Default: 🎉
banner.icon.size_gu
number
Sets the size of the banner icon, specified in grid units.
Default: 3
banner.color
text
Sets the banner component's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(50, 60, 200, 0.9)
banner.strokeColor
text
Sets the color of the outline drawn around the banner component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 30, 0.44)
banner.stroke_gu
number
Sets the width of the stroke drawn around the banner component. Specified in grid units.
Default: 0
banner.text.color
text
Sets the banner component's text color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
banner.text.strokeColor
text
Sets the color of the stroke drawn around the characters in the banner component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.1)
banner.text.stroke_gu
number
Sets the width of the stroke drawn around the characters in the banner component. Specified in grid units.
Default: 0.5
banner.text.fontFamily
string
Sets the font of text displayed in the banner component. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Roboto
banner.title.fontSize_gu
number
Sets the banner title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2
banner.title.fontWeight
string
Sets the banner title font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
banner.title.fontStyle
string
Sets the font style for the banner title. Valid options: 'normal','italic'.
Default:
banner.subtitle.fontSize_gu
number
Sets the banner subtitle font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 1.5
banner.subtitle.fontWeight
string
Sets the banner subtitle font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 300
banner.subtitle.fontStyle
string
Sets the font style for the banner subtitle. Valid options: 'normal','italic'.
Default:
Group: toast

toast.key
number
Triggers display of toast component. To send a toast, increment the value of key
Default: 0
toast.text
string
Sets text displayed in toast component.
Default: Hello world
toast.source
string
Sets the data source used for the text displayed in the toast component. The default value param means that the value of param toast.content is used. Valid options: param, chatMessages, transcript
Default: param
toast.duration_secs
number
Sets duration of time toast component is displayed (in seconds).
Default: 4
toast.maxW_pct_default
number
Sets the maximum width for the toast component, as a percentage of the viewport size.
Default: 50
toast.maxW_pct_portrait
number
Sets the maximum width for the toast component, as a percentage of the viewport size, applied only when the viewport aspect ratio is portrait (i.e. smaller than 1). This override is useful because on a narrow screen the toast display typically needs more horizontal space than on a landscape screen.
Default: 80
toast.showIcon
boolean
Sets whether icon is displayed in toast component (true or false).
Default: true
toast.icon.assetName
string
Sets asset value for toast icon. Icon asset must be included in session_assets object.
Default:
toast.icon.emoji
text
Sets an emoji to be rendered as the toast icon. If this string is non-empty, it will override toast.icon.assetName. The string value must be an emoji.
Default: 🎉
toast.icon.size_gu
number
Sets the size of the toast icon, in grid units.
Default: 3
toast.color
string
Sets the toast component's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(15, 50, 110, 0.6)
toast.strokeColor
string
Sets the color of the stroke drawn around the text characters in the toast component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 30, 0.44)
toast.text.color
string
Sets the toast component's text color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
toast.text.fontFamily
string
Sets the toast component's font family. Valid options: DMSans, Roboto, RobotoCondensed, Bitter, Exo, Magra, SuezOne, Teko
Default: Roboto
toast.text.fontWeight
number
Sets the font weight for the toast component's text. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
toast.text.fontSize_pct
number
Sets the font size for the toast component's text.
Default: 100
Group: openingSlate

openingSlate.duration_secs
number
Sets the number of seconds that the opening slate will be displayed when the stream starts. After this time, the slate goes away with a fade-out effect.
Default: 4
openingSlate.title
string
Sets text displayed in the main title of the opening slate.
Default: Welcome
openingSlate.subtitle
string
Sets text displayed in the subtitle (second line) of the opening slate.
Default:
openingSlate.bgImageAssetName
string
Sets an image to be used as the background for the slate. This image asset must be included in session_assets object when starting the stream/recording.
Default:
openingSlate.bgColor
string
Sets the slate's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 1)
openingSlate.textColor
string
Sets the text color of the titles in the slate. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 1)
openingSlate.fontFamily
string
Sets the font of the titles in the slate. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Bitter
openingSlate.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
openingSlate.fontStyle
string
Sets the font style for the titles in the slate. Valid options: 'normal','italic'.
Default:
openingSlate.fontSize_gu
number
Sets the main title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
openingSlate.subtitle.fontSize_pct
number
Sets the subtitle font size as a percentage of the main title.
Default: 75
openingSlate.subtitle.fontWeight
string
Selects a weight variant from the selected font family specifically for the subtitle. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 400
Group: titleSlate

titleSlate.enableTransition
boolean
Sets the slate to fade in or out when the showTitleSlate property is updated.'
Default: true
titleSlate.title
string
Sets text displayed in the main title of the slate.
Default: Title slate
titleSlate.subtitle
string
Sets text displayed in the subtitle (second line) of the slate.
Default: Subtitle
titleSlate.bgImageAssetName
string
Sets an image to be used as the background for the slate. This image asset must be included in session_assets object when starting the stream/recording.
Default:
titleSlate.bgColor
string
Sets the slate's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 1)
titleSlate.textColor
string
Sets the text color of the titles in the slate. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 1)
titleSlate.fontFamily
string
Sets the font of the titles in the slate. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Bitter
titleSlate.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
titleSlate.fontStyle
string
Sets the font style for the titles in the slate. Valid options: 'normal','italic'.
Default:
titleSlate.fontSize_gu
number
Sets the main title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
titleSlate.subtitle.fontSize_pct
number
Sets the subtitle font size as a percentage of the main title.
Default: 75
titleSlate.subtitle.fontWeight
string
Selects a weight variant from the selected font family specifically for the subtitle. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 400
Group: sidebar

sidebar.shrinkVideoLayout
boolean
Sets whether the sidebar is displayed on top of video elements. If set to true , the video layout is shrunk horizontally to make room for the sidebar so they don't overlap.
Default: false
sidebar.source
string
Sets the data source for the text displayed in the sidebar. Valid options: param, highlightLines.items, chatMessages, transcript
Default: highlightLines.items
sidebar.padding_gu
number
Padding inside the sidebar, specified in grid units.
Default: 1.5
sidebar.width_pct_landscape
number
Sets the width of the sidebar, as a percentage of the viewport size, applied when the viewport is landscape (its aspect ratio is greater than 1).
Default: 30
sidebar.height_pct_portrait
number
Sets the width of the sidebar, as a percentage of the viewport size, applied when the viewport is portrait or square (its aspect ratio is less than or equal to 1).
Default: 25
sidebar.bgColor
text
Sets the sidebar's background color and opacity. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 50, 0.55)
sidebar.textColor
text
Sets the sidebar's text color and opacity. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 0.94)
sidebar.fontFamily
string
Sets the font of text displayed in the sidebar. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: DMSans
sidebar.fontWeight
string
Sets the sidebar text font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 300
sidebar.fontStyle
string
Sets the font style for text in the sidebar. Valid options: 'normal','italic'.
Default:
sidebar.fontSize_gu
number
Sets the sidebar text font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 1.4
sidebar.textHighlight.color
text
Sets the color used for the highlighted item in the sidebar.
Default: rgba(255, 230, 0, 1)
sidebar.textHighlight.fontWeight
string
Sets the font weight used for the highlighted item in the sidebar.
Default: 600
Group: highlightLines

highlightLines.items
text
Sets a list of text items. Items must be separated by newline characters. This param is a data source that can be displayed in other components like TextOverlay, Banner and Sidebar using the various "source" params available in the settings for those components.
highlightLines.position
number
Sets the highlight index associated with the text items specified in highlightLines.items. The item at this index will be displayed using a special highlight style (which depends on the component used to display this data). If you don't want a highlight, set this value to -1.
Default: 0
Group: emojiReactions

emojiReactions.source
string
Sets the data source used for emoji reactions. The default value emojiReactions means that this component will display emojis that are sent via the standard source API.

The other valid option is param, which lets you send a reaction using param values instead of the standard source. The steps are as follows: set emojiReactions.source to param, set a single-emoji string for emojiReactions.emoji, and increment the value of emojiReactions.key to send one emoji for display.
Default: emojiReactions
emojiReactions.key
number
If emojiReactions.source is set to param, increment this numeric key to send a new emoji for display.
Default: 0
emojiReactions.emoji
text
If emojiReactions.source is set to param, set a single emoji as the string value for this param, and it will be the next emoji reaction rendered when emojiReactions.key is incremented.
Default:
emojiReactions.offset_x_gu
number
Sets a horizontal offset applied to the emoji reactions animation rendering (each new emoji floats up from the bottom of the screen). Specified in grid units.
Default: 0
Group: debug

debug.showRoomState
boolean
When set to true, a room state debugging display is visible. It prints various information about participant state.
Default: false
debug.overlayOpacity
number
Sets the opacity of the debugging display which can be toggled using debug.showRoomState.
Default: 90
Example requests


Default

Single Participant

Active Participant

Portrait

Custom

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"layout": {"preset": "default", "max_cam_streams": 1}}' \
     https://api.daily.co/v1/rooms/hello/recordings/update

POST /rooms/:name/recordings/stop
PAY-AS-YOU-GO

Stops a recording. Returns a 400 HTTP status code if no recording is active.

If multiple streaming instances are running, each instance must be stopped individually by a call to this endpoint with the instance's unique instanceId. If a "raw-tracks" recording is being used, a type must be declared of value "raw-tracks".

Path params

name
string
The name of the room.
Body params

instanceId
string
UUID for a streaming or recording session. Used when multiple streaming or recording sessions are running for single room.
type
string
The type of recording you are attempting to stop.
Options: "cloud","raw-tracks"
Default: cloud
Example requests


Request

With Instance Id

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST \
     https://api.daily.co/v1/rooms/hello/recordings/stop

POST
/rooms/:name/live-streaming/start

Receive a $15 credit for free
Try Daily pay-as-you-go features for free! New accounts have a $15 credit automatically applied when you add a credit card to the account. Learn more about pay-as-you-go features on our pricing page.
Starts a live stream at the rtmpUrl specified.

Multiple RTMP URLs can be passed using the endpoints property, which accepts an array of RTMP URLs. (See addLiveStreamingEndpoints() for a code example using this property.)

Cannot accept both rtmpURL and endpoints at the same time. Use endpoints when you want to start both RTMP and HLS.

Multiple streaming sessions (up to max_streaming_instances_per_room on your Daily domain) can be started by specifying a unique instanceId. Each instance can have a different layout, participants, lifetime, and update rules.

Contact us to configure max_streaming_instances_per_room for your domain. Note: recording and streaming instances that share the same instanceId also share the same underlying composition process, so any layout change made to streaming will also affect recording, and vice-versa.

A 503 status code may be returned if there are not enough workers available. In this case, you may retry the request again.

If you would like to use both RTMP and HLS, we recommend that you define streaming_endpoints for both types of endpoints.

Note: The outgoing RTMP stream has the following properties:

Resolution: 1920 x 1080
Frame rate: 30fps
Keyframe: every 2 seconds (60 frames)
Target bitrate: 5Mbps
Path params

name
string
The name of the room.
Body params

width
number
Property that specifies the output width of the given stream.
height
number
Property that specifies the output height of the given stream.
fps
number
Property that specifies the video frame rate per second.
videoBitrate
number
Property that specifies the video bitrate for the output video in kilobits per second (kbps).
audioBitrate
number
Property that specifies the audio bitrate for the output audio in kilobits per second (kbps).
minIdleTimeOut
number
Amount of time in seconds to wait before ending a recording or live stream when the room is idle (e.g. when all users have muted video and audio). Default: 300 (seconds). Note: Once the timeout has been reached, it typically takes an additional 1-3 minutes for the recording or live stream to be shut down.
maxDuration
number
Maximum duration in seconds after which recording/streaming is forcefully stopped. Default: `15000` seconds (3 hours). This is a preventive circuit breaker to prevent billing surprises in case a user starts recording/streaming and leaves the room.
backgroundColor
string
Specifies the background color of the stream, formatted as #rrggbb or #aarrggbb string.
instanceId
string
UUID for a streaming or recording session. Used when multiple streaming or recording sessions are running for single room.
layout
object
An object specifying the way participants’ videos are laid out in the live stream. See given layout configs for description of fields. Preset must be defined.
Default Layout

preset
string
Options: "default"
max_cam_streams
number
Single Participant Layout

preset
string
Options: "single-participant"
session_id
string
Active Participant Layout

preset
string
Options: "active-participant"
Portrait Layout

preset
string
Options: "portrait"
variant
string
Options: "vertical","inset"
max_cam_streams
number
Custom Layout

preset
string
Options: "custom"
composition_id
string
composition_params
object
session_assets
object
rtmpUrl
string | array
endpoints
array
Custom video layouts with VCS baseline composition

Daily offers a "baseline" composition option via the "custom" layout preset for customizing your video layouts while live streaming. This option allows for even more flexibility while using Daily's live streaming API.

Review our Video Component System (VCS) guide or VCS Simulator for additional information and code examples.
Many VCS properties use a "grid unit". The grid unit is a designer-friendly, device-independent unit. The default grid size is 1/36 of the output's minimum dimension. In other words, 1gu = 20px on a 720p stream and 30px on a 1080p stream. Learn more about grid units in our [VCS SDK docs](/reference/vcs/layout-api#the-grid-unit).

composition_params

mode
string
Sets the layout mode. Valid options:

single: Show a single full-screen video.
split: Show the first two participants side-by-side.
grid: Show up to 20 videos in a grid layout.
dominant: Show the active speaker in a large pane on the left, with additional video thumbnails on the right.
pip: Show the active speaker in a full-screen view, with the first participant inlaid in a corner.
Default: grid
showTextOverlay
boolean
Sets whether a text overlay is displayed. You can configure the contents of the overlay with the text.* properties.
Default: false
showImageOverlay
boolean
Sets whether an image overlay is displayed. You can configure the display of the overlay with the image.* properties. The image used must be passed in the session_id layout option when the stream or recording is started.
Default: false
showBannerOverlay
boolean
Sets whether a banner overlay is displayed. The banner can be used for TV-style "lower third" graphics, or displayed in any corner. You can configure the content of the overlay with the banner.* properties.
Default: false
showWebFrameOverlay
boolean
Sets whether a WebFrame overlay is displayed. You can configure the display of this live web browser overlay with the webFrame.* properties. The URL and the browser viewport size can be changed while your stream or recording is running.
Default: false
showSidebar
boolean
Sets whether a sidebar is displayed. You can configure the display of the sidebar with the sidebar.* properties.
Default: false
showTitleSlate
boolean
Sets whether a title screen (a "slate") is displayed. You can configure the display of the slate with the titleSlate.* properties.
Default: false
enableAutoOpeningSlate
boolean
Sets whether a title screen (a "slate") is automatically shown at the start of the stream. You can configure the display of this automatic slate with the openingSlate. properties.
Default: false
Group: videoSettings

videoSettings.maxCamStreams
number
Limits the number of non-screenshare streams that are included in the output.
Default: 25
videoSettings.preferredParticipantIds
string
Lets you do render-time reordering of video inputs according to participant IDs within a Daily room. To enable this sorting, pass a comma-separated list of participant IDs as the value for this param; video inputs matching these IDs will be moved to the top of the list. If you pass an ID that is not present in the room, it's ignored. All other video inputs will remain in their original order. The default value is an empty string indicating no reordering. Also note that videoSettings.preferScreenshare takes precedence over the ordering passed here. For more information about how participants and videos are sorted, see the section on selecting participants.
Default:
videoSettings.preferScreenshare
boolean
When enabled, screen share inputs will be sorted before camera inputs. This is useful when prioritizing screen shares in your layout, especially when all inputs are not included in the final stream. For more information about how participants and videos are sorted, see the section on selecting participants.
Default: false
videoSettings.omitPausedVideo
boolean
When enabled, paused video inputs will not be included. By default this is off, and paused inputs are displayed with a placeholder graphic. ("Paused video" means that the video track for a participant is not available, either due to user action or network conditions.)
Default: false
videoSettings.omitAudioOnly
boolean
When enabled, audio-only inputs will not be included in rendering. By default this is off, and audio participants are displayed with a placeholder graphic.
Default: false
videoSettings.omitExtraScreenshares
boolean
When enabled, any screenshare video inputs beyond the first one will not be included in rendering. You can control the ordering of the inputs using the layout.participants property to explicitly select which participant should be first in the list of inputs.
Default: false
videoSettings.showParticipantLabels
boolean
Sets whether call participants' names are displayed on their video tiles.
Default: false
videoSettings.roundedCorners
boolean
Sets whether to display video tiles with squared or rounded corners. Note that some modes (dominant and pip) have additional params to control whether the main video has rounded corners or not.
Default: false
videoSettings.cornerRadius_gu
number
Sets the corner radius applied to video layers when videoSettings.roundedCorners is enabled, in grid units.
Default: 1.2
videoSettings.scaleMode
string
Controls how source video is displayed inside a tile if they have different aspect ratios. Use 'fill' to crop the video to fill the entire tile. Use 'fit' to make sure the entire video fits inside the tile, adding letterboxes or pillarboxes as necessary.
Default: fill
videoSettings.scaleModeForScreenshare
string
Controls how a screenshare video is displayed inside a tile if they have different aspect ratios. Use 'fill' to crop the video to fill the entire tile. Use 'fit' to make sure the entire video fits inside the tile, adding letterboxes or pillarboxes as necessary.
Default: fit
videoSettings.placeholder.bgColor
string
Sets the background color for video placeholder tile. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgb(0, 50, 80)
videoSettings.highlight.color
string
Sets the highlight color. It's used as the border color to indicate the 'dominant' video input (typically the active speaker). Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgb(255, 255, 255)
videoSettings.highlight.stroke_gu
number
Sets the stroke width used to render a highlight border. See also 'videoSettings.highlight.color'. Specified in grid units.
Default: 0.2
videoSettings.split.margin_gu
number
Sets the visual margin between the two video layers shown in split mode, in grid units.
Default: 0
videoSettings.split.direction
string
Selects whether the 'split' layout mode is rendered in a horizontal or vertical configuration. The default value 'auto-by-viewport' means that the split direction will be automatically selected to be most appropriate for the current viewport size: if the viewport is landscape or square, the split axis is vertical; if portrait, the split axis is horizontal. Valid options: 'auto-by-viewport', 'vertical', 'horizontal'
Default: auto-by-viewport
videoSettings.split.scaleModeOverrides
string
Overrides the scaleMode setting for the split layout mode. Both sides of the split can have separately defined scale modes. Pass a comma-separated list such as fill, fit (this would set the left-hand side video to fill and the right-hand side video to fit). See documentation for the videoSettings.scaleMode parameter for the valid options. Note that this setting also overrides videoSettings.scaleModeForScreenshare.
Default:
videoSettings.grid.useDominantForSharing
boolean
When enabled, the layout will automatically switch to dominant mode from grid if a screenshare video input is available. By using this automatic behavior, you avoid having to manually switch the mode via an API call.
Default: false
videoSettings.grid.itemInterval_gu
number
Overrides the visual margin between items in grid mode, in grid units. The default value of -1 means that the layout algorithm selects a reasonable margin automatically depending on the number of videos.
Default: -1
videoSettings.grid.outerPadding_gu
number
Overrides the outer padding around items in grid mode, in grid units. The default value of -1 means that the layout algorithm selects a reasonable padding automatically depending on the number of videos.
Default: -1
videoSettings.grid.highlightDominant
boolean
By default, the grid mode will highlight the dominant video (typically the "active speaker") with a light outline. You can disable the highlight using this setting.
Default: true
videoSettings.grid.preserveAspectRatio
boolean
By default, the layout for the grid mode will try to preserve the aspect ratio of the input videos, i.e. avoid cropping the videos and instead add margins around the grid if needed. Setting this parameter to false will make the grid layout fill all available area, potentially cropping the videos.
Default: true
videoSettings.dominant.position
string
Control where the dominant (or "active speaker") video is displayed in the dominant layout mode. Values are left, right, top or bottom.
Default: left
videoSettings.dominant.splitPos
number
Sets the position of the imaginary line separating the dominant video from the smaller tiles when using the dominant layout. Values are from 0 to 1. The default is 0.8, so if videoSettings.dominant.position is set to left, the dominant video will take 80% of the width of the screen on the left.
Default: 0.8
videoSettings.dominant.numChiclets
number
Controls how many "chiclets", or smaller video tiles, appear alongside the dominant video when using the dominant layout.
Default: 5
videoSettings.dominant.followDomFlag
boolean
When in dominant mode, the large tile displays the active speaker by default. Turn off this followDomFlag to display the first participant instead of the active speaker.
Default: true
videoSettings.dominant.itemInterval_gu
number
Margin between the “chiclet” items, in grid units.
Default: 0.7
videoSettings.dominant.outerPadding_gu
number
Padding around the row/column of “chiclet” items, in grid units.
Default: 0.5
videoSettings.dominant.splitMargin_gu
number
Margin between the "dominant" video and the row/column of "chiclet" items, in grid units.
Default: 0
videoSettings.dominant.sharpCornersOnMain
boolean
Sets whether the "dominant" video will be rendered with rounded corners when videoSettings.roundedCorners is enabled. Defaults to false because sharp corners are a more natural choice for the default configuration where the dominant video is tightly aligned to viewport edges.
Default: true
videoSettings.pip.position
string
Sets the position of the smaller video in the pip (picture-in-picture) layout. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'.
Default: top-right
videoSettings.pip.aspectRatio
number
Sets the aspect ratio of the smaller video in the pip layout. The default is 1.0, which produces a square video.
Default: 1
videoSettings.pip.height_gu
number
Sets the height of the smaller video in the pip layout, measured in grid units.
Default: 12
videoSettings.pip.margin_gu
number
Sets the margin between the smaller video and the edge of the frame in the pip layout, in grid units.
Default: 1.5
videoSettings.pip.followDomFlag
boolean
When in "pip" (or picture-in-picture) mode, the overlay tile displays the first participant in the participant array by default. Turn on this followDomFlag to display the active speaker instead.
Default: false
videoSettings.pip.sharpCornersOnMain
boolean
Sets whether the main video in pip mode will be rendered with rounded corners when videoSettings.roundedCorners is enabled. Defaults to false because sharp corners are a more natural choice for the default configuration where the main video is full-screen (no margin to viewport edges).
Default: true
videoSettings.labels.fontFamily
string
Sets the participant label style option: font family. Valid options: DMSans, Roboto, RobotoCondensed, Bitter, Exo, Magra, SuezOne, Teko
Default: Roboto
videoSettings.labels.fontWeight
string
Sets the participant label text font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 600
videoSettings.labels.fontSize_pct
number
Sets the participant label text font size.
Default: 100
videoSettings.labels.offset_x_gu
number
Sets the offset value for participant labels on the x-axis, measured in grid units.
Default: 0
videoSettings.labels.offset_y_gu
number
Sets the offset value for participant labels on the y-axis, measured in grid units.
Default: 0
videoSettings.labels.color
string
Sets the participant label font color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
videoSettings.labels.strokeColor
string
Sets the label font stroke color (the line outlining the text letters). Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.9)
videoSettings.margin.left_gu
number
Sets the left margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.right_gu
number
Sets the right margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.top_gu
number
Sets the top margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
videoSettings.margin.bottom_gu
number
Sets the bottom margin value applied to videos (in any layout mode), in grid units. You can use these videoSettings.margin.* params to shrink the video area, for example to make room for overlays.
Default: 0
Group: text

text.content
string
Sets the string to be displayed if showTextOverlay is true.
Default:
text.source
string
Sets the data source used for the text displayed in the overlay. The default value 'param' means that the value of param text.content is used. Valid options: param, highlightLines.items, chatMessages, transcript
Default: param
text.align_horizontal
string
Sets the horizontal alignment of the text overlay within the video frame. Values are left, right, or center.
Default: center
text.align_vertical
string
Sets the vertical alignment of the text overlay within the video frame. Values are top, bottom, or center.
Default: center
text.offset_x_gu
number
Sets an x-offset (horizontal) to be applied to the text overlay's position based on the values of text.align_horizontal and text.align_vertical.
Default: 0
text.offset_y_gu
number
Sets a y-offset (vertical) to be applied to the text overlay's position based on the values of text.align_horizontal and text.align_vertical.
Default: 0
text.rotation_deg
number
Applies a rotation to the text overlay. Units are degrees, and positive is a clockwise rotation.
Default: 0
text.fontFamily
string
Sets the font of the text overlay. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: DMSans
text.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
text.fontStyle
string
Sets the font style for text. Valid options: 'normal','italic'.
Default:
text.fontSize_gu
number
Sets the text overlay font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
text.color
string
Sets the color and transparency of the text overlay. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 250, 200, 0.95)
text.strokeColor
string
Sets the color of the stroke drawn around the characters in the text overlay. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.8)
text.stroke_gu
number
Sets the width of the stroke drawn around the characters in the text overlay. Specified in grid units.
Default: 0.5
text.highlight.color
text
Sets the color and transparency of a highlighted item in the text overlay. To display a highlight, the value of param text.source must be set to highlightLines.items. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 0, 1)
text.highlight.fontWeight
enum
Sets the font weight of a highlighted item in the text overlay. To display a highlight, the value of param text.source must be set to highlightLines.items.
Default: 700
Group: image

image.assetName
string
Sets the overlay image. Icon asset must be included in session_assets object. showImageOverlay must be true.
Default: overlay.png
image.emoji
text
Sets an emoji to be rendered instead of an image asset. If this string is non-empty, it will override the value of image.assetName. The string value must be an emoji.
Default:
image.position
string
Sets position of overlay image. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
Default: top-right
image.fullScreen
boolean
Sets overlay image to full screen.
Default: false
image.aspectRatio
number
Sets aspect ratio of overlay image.
Default: 1.778
image.height_gu
number
Sets height of overlay image, in grid units.
Default: 12
image.margin_gu
number
Sets margin between the overlay image and the viewport edge, in grid units.
Default: 1.5
image.opacity
number
Sets opacity of overlay image, in range 0-1. Default value of 1 is full opacity.
Default: 1
image.enableFade
boolean
Sets the overlay image to fade in or out when the showImageOverlay property is updated.
Default: true
Group: webFrame

webFrame.url
string
Sets the web page URL to be loaded into the WebFrame overlay's embedded browser.
Default:
webFrame.viewportWidth_px
number
Sets the width of the embedded browser window used to render the WebFrame overlay.
Default: 1280
webFrame.viewportHeight_px
number
Sets the height of the embedded browser window used to render the WebFrame overlay.
Default: 720
webFrame.position
string
Sets position of the WebFrame overlay. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
Default: top-right
webFrame.fullScreen
boolean
Sets the WebFrame overlay to full screen.
Default: false
webFrame.height_gu
number
Sets height of the WebFrame overlay, in grid units.
Default: 12
webFrame.margin_gu
number
Sets margin between the WebFrame overlay and the viewport edge, in grid units.
Default: 1.5
webFrame.opacity
number
Sets opacity of the WebFrame overlay, in range 0-1. Default value of 1 is full opacity.
Default: 1
webFrame.enableFade
boolean
Sets the WebFrame overlay to fade in or out when the showWebFrameOverlay property is updated.
Default: true
webFrame.keyPress.keyName
string
Sets the keyboard key to be sent to the WebFrame browser in a simulated key press. Valid options:

Digits 0 - 9
Letters A - Z
ASCII special characters, e.g. !, @, +, >, etc.
Function keys F1 - F12
Enter
Escape
Backspace
Tab
Arrow keys ArrowUp, ArrowDown, ArrowLeft, ArrowRight
PageDown, PageUp
Default: ArrowRight
webFrame.keyPress.modifiers
string
Sets keyboard modifier keys to be sent to the WebFrame browser in a simulated key press. Valid options: "Shift", "Control", "Alt", "Meta" (on a Mac keyboard, Alt is equal to Option and Meta is equal to Command).
Default:
webFrame.keyPress.key
number
Triggers a simulated key press to be sent to WebFrame. To send a key press, increment the value of key. (Note the difference between this and keyName which is the simulated key to be sent.)
Default: 0
Group: banner

banner.title
text
Sets the title text displayed in the banner component.
Default: Hello world
banner.subtitle
text
Sets the subtitle text displayed in the banner component.
Default: This is an example subtitle
banner.source
string
Sets the data source for the text displayed in the banner component. Valid options: param, highlightLines.items, chatMessages, transcript
Default: param
banner.position
string
Sets position of the banner component. Valid options: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
banner.enableTransition
boolean
Sets the banner to fade in or out when the showBannerOverlay property is updated.
Default: true
banner.margin_x_gu
number
Horizontal margin, specified in grid units.
Default: 0
banner.margin_y_gu
number
Vertical margin, specified in grid units.
Default: 1
banner.padding_gu
number
Padding inside the component, specified in grid units.
Default: 2
banner.alwaysUseMaxW
boolean
Sets whether the banner component will always use its maximum width (specified using banner.maxW_pct_default and banner.maxW_pct_portrait). If false, the banner component will shrink horizontally to fit text inside it, if appropriate.
Default: false
banner.maxW_pct_default
number
Sets the maximum width for the banner component, as a percentage of the viewport size.
Default: 65
banner.maxW_pct_portrait
number
Sets the maximum width for the banner component, as a percentage of the viewport size, applied only when the viewport aspect ratio is portrait (i.e. smaller than 1). This override is useful because on a narrow screen the banner display typically needs more horizontal space than on a landscape screen.
Default: 90
banner.rotation_deg
number
Applies a rotation to the banner component. Units are degrees, and positive is a clockwise rotation.
Default: 0
banner.cornerRadius_gu
number
Sets the corner radius of the banner component outline. Specified in grid units.
Default: 0
banner.showIcon
boolean
Sets whether an icon is displayed in the banner component (true or false).
Default: true
banner.icon.assetName
text
Sets image asset value for the banner icon. Icon asset must be included in session_assets object.
Default:
banner.icon.emoji
text
Sets an emoji to be rendered as the banner icon. If this string is non-empty, it will override banner.icon.assetName. The string value must be an emoji.
Default: 🎉
banner.icon.size_gu
number
Sets the size of the banner icon, specified in grid units.
Default: 3
banner.color
text
Sets the banner component's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(50, 60, 200, 0.9)
banner.strokeColor
text
Sets the color of the outline drawn around the banner component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 30, 0.44)
banner.stroke_gu
number
Sets the width of the stroke drawn around the banner component. Specified in grid units.
Default: 0
banner.text.color
text
Sets the banner component's text color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
banner.text.strokeColor
text
Sets the color of the stroke drawn around the characters in the banner component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 0.1)
banner.text.stroke_gu
number
Sets the width of the stroke drawn around the characters in the banner component. Specified in grid units.
Default: 0.5
banner.text.fontFamily
string
Sets the font of text displayed in the banner component. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Roboto
banner.title.fontSize_gu
number
Sets the banner title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2
banner.title.fontWeight
string
Sets the banner title font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
banner.title.fontStyle
string
Sets the font style for the banner title. Valid options: 'normal','italic'.
Default:
banner.subtitle.fontSize_gu
number
Sets the banner subtitle font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 1.5
banner.subtitle.fontWeight
string
Sets the banner subtitle font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 300
banner.subtitle.fontStyle
string
Sets the font style for the banner subtitle. Valid options: 'normal','italic'.
Default:
Group: toast

toast.key
number
Triggers display of toast component. To send a toast, increment the value of key
Default: 0
toast.text
string
Sets text displayed in toast component.
Default: Hello world
toast.source
string
Sets the data source used for the text displayed in the toast component. The default value param means that the value of param toast.content is used. Valid options: param, chatMessages, transcript
Default: param
toast.duration_secs
number
Sets duration of time toast component is displayed (in seconds).
Default: 4
toast.maxW_pct_default
number
Sets the maximum width for the toast component, as a percentage of the viewport size.
Default: 50
toast.maxW_pct_portrait
number
Sets the maximum width for the toast component, as a percentage of the viewport size, applied only when the viewport aspect ratio is portrait (i.e. smaller than 1). This override is useful because on a narrow screen the toast display typically needs more horizontal space than on a landscape screen.
Default: 80
toast.showIcon
boolean
Sets whether icon is displayed in toast component (true or false).
Default: true
toast.icon.assetName
string
Sets asset value for toast icon. Icon asset must be included in session_assets object.
Default:
toast.icon.emoji
text
Sets an emoji to be rendered as the toast icon. If this string is non-empty, it will override toast.icon.assetName. The string value must be an emoji.
Default: 🎉
toast.icon.size_gu
number
Sets the size of the toast icon, in grid units.
Default: 3
toast.color
string
Sets the toast component's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(15, 50, 110, 0.6)
toast.strokeColor
string
Sets the color of the stroke drawn around the text characters in the toast component. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 30, 0.44)
toast.text.color
string
Sets the toast component's text color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: white
toast.text.fontFamily
string
Sets the toast component's font family. Valid options: DMSans, Roboto, RobotoCondensed, Bitter, Exo, Magra, SuezOne, Teko
Default: Roboto
toast.text.fontWeight
number
Sets the font weight for the toast component's text. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
toast.text.fontSize_pct
number
Sets the font size for the toast component's text.
Default: 100
Group: openingSlate

openingSlate.duration_secs
number
Sets the number of seconds that the opening slate will be displayed when the stream starts. After this time, the slate goes away with a fade-out effect.
Default: 4
openingSlate.title
string
Sets text displayed in the main title of the opening slate.
Default: Welcome
openingSlate.subtitle
string
Sets text displayed in the subtitle (second line) of the opening slate.
Default:
openingSlate.bgImageAssetName
string
Sets an image to be used as the background for the slate. This image asset must be included in session_assets object when starting the stream/recording.
Default:
openingSlate.bgColor
string
Sets the slate's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 1)
openingSlate.textColor
string
Sets the text color of the titles in the slate. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 1)
openingSlate.fontFamily
string
Sets the font of the titles in the slate. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Bitter
openingSlate.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
openingSlate.fontStyle
string
Sets the font style for the titles in the slate. Valid options: 'normal','italic'.
Default:
openingSlate.fontSize_gu
number
Sets the main title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
openingSlate.subtitle.fontSize_pct
number
Sets the subtitle font size as a percentage of the main title.
Default: 75
openingSlate.subtitle.fontWeight
string
Selects a weight variant from the selected font family specifically for the subtitle. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 400
Group: titleSlate

titleSlate.enableTransition
boolean
Sets the slate to fade in or out when the showTitleSlate property is updated.'
Default: true
titleSlate.title
string
Sets text displayed in the main title of the slate.
Default: Title slate
titleSlate.subtitle
string
Sets text displayed in the subtitle (second line) of the slate.
Default: Subtitle
titleSlate.bgImageAssetName
string
Sets an image to be used as the background for the slate. This image asset must be included in session_assets object when starting the stream/recording.
Default:
titleSlate.bgColor
string
Sets the slate's background color. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 0, 1)
titleSlate.textColor
string
Sets the text color of the titles in the slate. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 1)
titleSlate.fontFamily
string
Sets the font of the titles in the slate. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: Bitter
titleSlate.fontWeight
string
Selects a weight variant from the selected font family. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 500
titleSlate.fontStyle
string
Sets the font style for the titles in the slate. Valid options: 'normal','italic'.
Default:
titleSlate.fontSize_gu
number
Sets the main title font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 2.5
titleSlate.subtitle.fontSize_pct
number
Sets the subtitle font size as a percentage of the main title.
Default: 75
titleSlate.subtitle.fontWeight
string
Selects a weight variant from the selected font family specifically for the subtitle. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 400
Group: sidebar

sidebar.shrinkVideoLayout
boolean
Sets whether the sidebar is displayed on top of video elements. If set to true , the video layout is shrunk horizontally to make room for the sidebar so they don't overlap.
Default: false
sidebar.source
string
Sets the data source for the text displayed in the sidebar. Valid options: param, highlightLines.items, chatMessages, transcript
Default: highlightLines.items
sidebar.padding_gu
number
Padding inside the sidebar, specified in grid units.
Default: 1.5
sidebar.width_pct_landscape
number
Sets the width of the sidebar, as a percentage of the viewport size, applied when the viewport is landscape (its aspect ratio is greater than 1).
Default: 30
sidebar.height_pct_portrait
number
Sets the width of the sidebar, as a percentage of the viewport size, applied when the viewport is portrait or square (its aspect ratio is less than or equal to 1).
Default: 25
sidebar.bgColor
text
Sets the sidebar's background color and opacity. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(0, 0, 50, 0.55)
sidebar.textColor
text
Sets the sidebar's text color and opacity. Valid options:

Hex color codes
RGB or RGBA syntax
Standard CSS color names (e.g. 'blue')
Default: rgba(255, 255, 255, 0.94)
sidebar.fontFamily
string
Sets the font of text displayed in the sidebar. Valid options: DMSans, Roboto, RobotoCondensed, Anton, Bangers, Bitter, Exo, Magra, PermanentMarker, SuezOne, Teko
Default: DMSans
sidebar.fontWeight
string
Sets the sidebar text font weight. Valid options: 100, 200, 300, 400, 500, 600, 700, 800, 900.

Note: Not all font weights are valid for every font family.
Default: 300
sidebar.fontStyle
string
Sets the font style for text in the sidebar. Valid options: 'normal','italic'.
Default:
sidebar.fontSize_gu
number
Sets the sidebar text font size using grid units (gu). By default, one grid unit is 1/36 of the smaller dimension of the viewport (e.g. 20px in a 1280*720 stream).
Default: 1.4
sidebar.textHighlight.color
text
Sets the color used for the highlighted item in the sidebar.
Default: rgba(255, 230, 0, 1)
sidebar.textHighlight.fontWeight
string
Sets the font weight used for the highlighted item in the sidebar.
Default: 600
Group: highlightLines

highlightLines.items
text
Sets a list of text items. Items must be separated by newline characters. This param is a data source that can be displayed in other components like TextOverlay, Banner and Sidebar using the various "source" params available in the settings for those components.
highlightLines.position
number
Sets the highlight index associated with the text items specified in highlightLines.items. The item at this index will be displayed using a special highlight style (which depends on the component used to display this data). If you don't want a highlight, set this value to -1.
Default: 0
Group: emojiReactions

emojiReactions.source
string
Sets the data source used for emoji reactions. The default value emojiReactions means that this component will display emojis that are sent via the standard source API.

The other valid option is param, which lets you send a reaction using param values instead of the standard source. The steps are as follows: set emojiReactions.source to param, set a single-emoji string for emojiReactions.emoji, and increment the value of emojiReactions.key to send one emoji for display.
Default: emojiReactions
emojiReactions.key
number
If emojiReactions.source is set to param, increment this numeric key to send a new emoji for display.
Default: 0
emojiReactions.emoji
text
If emojiReactions.source is set to param, set a single emoji as the string value for this param, and it will be the next emoji reaction rendered when emojiReactions.key is incremented.
Default:
emojiReactions.offset_x_gu
number
Sets a horizontal offset applied to the emoji reactions animation rendering (each new emoji floats up from the bottom of the screen). Specified in grid units.
Default: 0
Group: debug

debug.showRoomState
boolean
When set to true, a room state debugging display is visible. It prints various information about participant state.
Default: false
debug.overlayOpacity
number
Sets the opacity of the debugging display which can be toggled using debug.showRoomState.
Default: 90
Selecting participants

The baseline composition has several modes that display multiple participant videos. You may be wondering how to control which participants appear in specific places within those layouts.

Internally, VCS uses an ordered array of video inputs that it calls "video input slots". By default, that array will contain all participants in the order in which they joined the call. But there are two ways you can override this default behavior and choose which participants appear in your layout:

Participant selection on the room level using the participants property.
Input reordering on the composition level (a.k.a. switching) using the preferredParticipantIds and preferScreenshare params available in the baseline composition.
These two are not mutually exclusive. What's the difference, and when should you use one or the other?

Room-level participant selection is a powerful generic tool. It lets you choose any participants within the room, and will trigger any necessary backend connections so that a participant's audio and video streams become available to the VCS rendering server. This means there may be a slight delay as connections are made.

In contrast, composition-level input reordering (a.k.a. switching) happens at the very last moment in the VCS engine just before a video frame is rendered. (The name "switching" refers to a video switcher, a hardware device used in traditional video production for this kind of input control.) It's applied together with any other composition param updates you're sending, so there is a guarantee of synchronization. You should use this method when you want to ensure that the reordering of inputs happens precisely at the same time as your update to some other composition param value(s). For example, if you're switching a layout mode and want the inputs to be sorted in a different way simultaneously.

You can use the two methods together. Room-level selection using the participants property lets you establish the participants whose streams will be available to the rendering. You can then do rapid switching within that selection using the preferredParticipantIds and preferScreenshare params in the baseline composition.

Here's an example of selecting three specific participant video tracks, everyone's audio tracks, and sorting the video by most recent active speaker:

JavaScript
Copy to clipboard
{
    layout: {
        preset: "custom",
        composition_params: {...},
        participants: {
            video: ["participant-guid-1", "participant-guid-2", "participant-guid-3"],
            audio: ["*"],
            sort: "active"
        }
    }
}

Here's another example where we're further sorting the same video tracks using the baseline composition params. The params update is switching to a different layout mode ('split'). This mode can only show two participants, so we use videoSettings.preferredParticipantIds to select the two participants in a clean frame-synchronized way, without having to modify the underlying connections made via the participants property:

JavaScript
Copy to clipboard
{
    layout: {
        preset: "custom",
        composition_params: {
            mode: 'split',
            'videoSettings.preferredParticipantIds': 'participant-guid-2, participant-guid-1',
        },
        participants: {
            video: ["participant-guid-1", "participant-guid-2", "participant-guid-3"],
            audio: ["*"],
            sort: "active"
        }
    }
}

If you include the participants object in a startLiveStreaming()/startRecording() or updateLiveStreaming()/updateRecording() call, you need to include it in any subsequent updateLiveStreaming()/updateRecording() calls as well, even if you aren't changing it.
If you set the participants property for your recording or live stream and then make an updateLiveStreaming()/updateRecording() call to update the composition_params, you'll need to resend the same values you used before in the participants property. This is true even if you are not updating the participants property. If you don't, the participant configuration will reset to default, as if you hadn't set it in the first place —meaning VCS will receive all audio and video tracks from all participants, sorted by the order in which the participants joined the call.
participants properties

video
array
Required. An array of strings indicating which participant videos to make available to VCS. Possible values are:

["participant-guid-1", "participant-guid-2", "participant-guid-3"]: A list of specific participant IDs
["*"]: everyone
["owners"]: All call owners
audio
array
An optional array of strings indicating which participant audio tracks to make available to VCS. Possible values are the same as the video property.
sort
string
The only currently valid value for this property is "active". This property controls the order in which VCS sees the participant video tracks. When set to "active", each time the call's active speaker changes to a different participant, that participant will bubble up to the first position in the array. In other words, setting sort to "active" will cause an n-tile layout to always show the n most recent speakers in the call. If you leave the property unset, the list of participants will stay in a fixed order: either the order you specified in the video property, or in the order they joined the call if you use "*" or "owners".
Session assets

Session assets — images or custom VCS components — that can be passed as assets and used during a live stream or cloud recording. To learn more, visit our Session assets page in the VCS SDK reference docs.

Note: Session assets must be made available at the beginning of the recording or live stream even if they are not used until later in the call.

Example requests


Default

Single Participant

Active Participant

Portrait

Custom

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XPOST -d '{"layout": {"preset": "default", "max_cam_streams": 1}}' \
     https://api.daily.co/v1/rooms/hello/live-streaming/start


The "meeting token" object
"Meeting tokens" control room access and session configuration on a per-user basis.

A participant can join a non-public room with a valid meeting token. For private or public rooms, you can use meeting tokens to configure how a participant experiences the meeting (e.g. what call features are available).

You can create and validate meeting tokens.

JSON
Copy to clipboard
{
  // example meeting token object
  "exp": 1548633621,
  "room_name": "hello",
  "user_name": "A. User",
  "is_owner": true,
  "close_tab_on_exit": true,
  "enable_recording": "cloud",
  "start_video_off": true
}

Meeting token configuration properties set three things: room access, meeting time limits, and participant details, including their meeting permissions and available features.

Room access

room_name

Always set room_name
A meeting token without a room_name property allows access to any room in your domain. Always set the room_name property when you are using meeting tokens to control room access.
See our guide to controlling room access for more details.
Your tokens are unique to your domain and rooms. Tokens from another Daily domain can never grant access to your rooms.

Meeting time limits

Two properties control how long a user is allowed to stay in a meeting.

If eject_at_token_exp is set to true, the user is kicked out of the meeting when the token expires. If the room is not public, then the user will not be able to rejoin the room.

The eject_after_elapsed property is the maximum number of seconds the user can stay in the meeting. The user will be kicked out eject_after_elapsed seconds after joining the meeting. If the meeting token has expired (and the room is not public) the user will not be able to rejoin the room. If the meeting token hasn't expired, of course, the user could reuse the meeting link and token to rejoin the room.

The two token properties eject_at_token_exp and eject_after_elapsed override the two room properties eject_at_room_exp and eject_after_elapsed. If either of the token properties are set, the two room properties are completely ignored for the current meeting session.

Meeting time limits tutorial
Add advanced security to video chats with the Daily API
Participant details, meeting permissions, and available features

You can use tokens to configure when a participant can join a meeting, when their access expires, and the call features that are enabled for each participant in a meeting. For example, you could set up a virtual classroom so that only one participant in the meeting (the teacher) can broadcast audio and video (to the students).

nbf
exp
is_owner
user_name
user_id
enable_screenshare
start_video_off
start_audio_off
enable_recording
start_cloud_recording 
PAY-AS-YOU-GO
close_tab_on_exit
redirect_on_meeting_exit
lang
For a full descriptions of all properties, please see the table below.

Using meeting tokens

To use a meeting token, pass it as a property to the factory method of your choice, or via the join() method.

Setting a meeting token for a call participant via a factory or join() method property is the only way Daily recommends using meeting tokens, for security reasons.
For example, to give a specific participant special access when they join a meeting (e.g. admin privileges), you'd write something like:

JavaScript
Copy to clipboard
// example passing meeting token in join method
call.join({
  url: 'DAILY_ROOM_URL',
  token: 'DAILY_MEETING_TOKEN',
});

Heads up!
Don't forget to generate your meeting tokens server-side to keep production applications secure.
Read about how to set up an instant Daily server with Node.js and Glitch.
Under the covers, meeting tokens are JSON Web Tokens. They are signed, but not encrypted, so you can decode the raw token yourself, if you're interested. Note that this means you should never put information that you want to keep secure into a meeting token.

You don't ever need to delete a meeting token. Meeting tokens are just cryptographically signed chunks of information that are validated by our API endpoints; they don't exist as server-side resources.
Configuration
Many room configuration fields are also available as meeting token fields. If a configuration field is set for both the room and the user's meeting token, the token setting takes precedence. Learn more in our blog post on this topic.
Daily strongly recommends adding room_name and exp values to all meeting tokens to improve app security. Read more on the Daily blog.
room_name
string
The room for which this token is valid. If room_name isn't set, the token is valid for all rooms in your domain. *You should always set room_name if you are using this token to control access to a meeting.
eject_at_token_exp
boolean
Kick this user out of the meeting at the time this meeting token expires. If either this property or eject_after_elapsed are set for the token, the room's eject properties are overridden.

See an example in our advanced security tutorial.
Default: false
eject_after_elapsed
integer
Kick this user out of the meeting this many seconds after they join the meeting. If either this property or eject_at_token_exp are set for the token, the room's eject properties are overridden.

See an example in our advanced security tutorial.
nbf
integer
"Not before". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in with this token before this time.
exp
integer
"Expires". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting with this token after this time.

Daily strongly recommends adding an exp value to all meeting tokens. Learn more in our Daily blog post: Add advanced security to video chats with the Daily API
is_owner
boolean
The user has meeting owner privileges. For example, if the room is configured for owner_only_broadcast and used in a Daily Prebuilt call, this user can send video, and audio, and can screenshare.
Default: false
user_name
string
The user's name in this meeting. The name displays in the user interface when the user is muted or has turned off the camera, and in the chat window. This username is also saved in the meeting events log (meeting events are retrievable using the analytics API methods.)
user_id
string
The user's ID for this meeting session. During a session, this ID is retrievable in the participants() method and related participant events. Either during or after a session concludes, this ID is retrievable using the /meetings REST API endpoint. You can use user_id to map between your user database and meeting events/attendance.

For domains configured for HIPAA compliance, if the user_id value is a UUID (for example, f81d4fae-7dec-11d0-a765-00a0c91e6bf6), then the UUID will be returned for the participant in the /meetings REST API endpoint. Otherwise, the string hipaa will be returned in order to remove potential PHI. During a session, the provided user_id will always be returned through the participants() method and related events, regardless of the user_id value.

The user_id has a limit of 36 characters.
enable_screenshare
boolean
Sets whether or not the user is allowed to screen share. This setting applies for the duration of the meeting. If you're looking to dynamically control whether a user can screen share during a meeting, then use the permissions token property.
Default: true
start_video_off
boolean
Disable the default behavior of automatically turning on a participant's camera on a direct join() (i.e. without startCamera() first).
Default: false
start_audio_off
boolean
Disable the default behavior of automatically turning on a participant's microphone on a direct join() (i.e. without startCamera() first).
Default: false
enable_recording
string
Jump to recording docs.
Options: "cloud","local","raw-tracks"
enable_prejoin_ui
boolean
Determines whether the participant using the meeting token enters a waiting room with a camera, mic, and browser check before joining a call. If this property is also set in the room or domain's configuration, the meeting token's configuration will take priority.

⚠️ You must be using Daily Prebuilt to use enable_prejoin_ui.
enable_live_captions_ui
boolean
Sets whether the participant sees a closed captions button in their Daily Prebuilt call tray. When the closed caption button is clicked, closed captions are displayed locally.

When set to true, a closed captions button appears in the call tray. When set to false, the closed captions button is hidden from the call tray.

Note: Transcription must be enabled for the room or users must have permission to start transcription for this feature to be enabled. View the transcription guide for more details.

⚠️ You must be using Daily Prebuilt to use enable_live_captions_ui.
enable_recording_ui
boolean
Determines whether the participant using the meeting token can see the Recording button in Daily Prebuilt's UI, which can be found in the video call tray. If this value is false, the button will not be included in the tray. If it's true, the Recording button will be displayed.

This option is useful when only specific call participants should have recording permissions.

⚠️ You must be using Daily Prebuilt to use enable_recording_ui.
enable_terse_logging
boolean
Reduces the volume of log messages. This feature should be enabled when there are more than 200 participants in a meeting to help improve performance.

See our guides for supporting large experiences for additional instruction.
Default: false
knocking
boolean
Requires the enable_knocking property to be set on the room. By default, if a user joins a room with enable_knocking set, and with a token, they will bypass the waiting screen and join the room directly. If this property is set to true, the user will be required to request access, and the owner will need to accept them before they can join.
Default: false
start_cloud_recording
boolean
PAY-AS-YOU-GO
Start cloud recording when the user joins the room. This can be used to always record and archive meetings, for example in a customer support context.

Note: This requires the enable_recording property of the room or token to be set to cloud. If you want to automatically record calls with other recording modes, use callObject.startRecording() after await callObject.join() in your code.
Default: false
start_cloud_recording_opts
object
PAY-AS-YOU-GO
Options for use when start_cloud_recording is true. See startRecording for available options.

⚠️ Specifying too many options may cause the token size to be very large. It is recommended to use token less than 2048 characters. For complex usecases, use the daily-js API.
auto_start_transcription
boolean
PAY-AS-YOU-GO
Start transcription when an owner joins the room. This property can be used to always transcribe meetings once an owner joins.
Default: false
close_tab_on_exit
boolean
(For meetings that open in a separate browser tab.) When a user leaves a meeting using the button in the in-call menu bar, the browser tab closes. This can be a good way, especially on mobile, for users to be returned to a previous website flow after a call.
Default: false
redirect_on_meeting_exit
string
(For meetings that open in a separate browser tab.) When a user leaves a meeting using the button in the in-call menu bar, the browser loads this URL. A query string that includes a parameter of the form recent-call=<domain>/<room> is appended to the URL. On mobile, you can redirect to a deep link to bring a user back into your app.
lang
string
The default language of the Daily prebuilt video call UI, for this room.

Setting the language at the token level will override any room or domain-level language settings you have.

Read more about changing prebuilt UI language settings.

* Norwegian "no" and Russian "ru" are only available in the new Daily Prebuilt.
Options: "da","de","en","es","fi","fr","it","jp","ka","nl","no","pt","pt-BR","pl","ru","sv","tr","user"
Default: en
permissions
object
Specifies the initial default permissions for a non-meeting-owner participant joining a call.

Each permission (i.e. each of the properties listed below) can be configured in the meeting token, the room, and/or the domain, in decreasing order of precedence.

Participant admins (those with the 'participants' value in their canAdmin permission) can also change participants' permissions on the fly during a call using updateParticipant() or updateParticipants().
hasPresence
boolean
Whether the participant appears as "present" in the call, i.e. whether they appear in participants().
canSend
boolean | array
Which types of media a participant should be permitted to send.

Can be:

An Array containing any of 'video', 'audio', 'screenVideo', and 'screenAudio'
true (meaning "all")
false (meaning "none")
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
boolean | array
Which admin tasks a participant is permitted to do.

Can be:

An array containing any of 'participants', 'streaming', or 'transcription'
true (meaning "all")
false (meaning "none")

Self-signing tokens
If you're unfamiliar with JWTs and how to create them, please use the existing /meeting-tokens endpoints.
Generating self-signed tokens

Using your API key, you can self-sign tokens that will be accepted by the backend, as long as the API key is still active at the time it is checked. This saves making a round-trip to the Daily API to generate tokens, which is great if you need to update the tokens often or create them in bulk.

You can create a JWT using your domain's API key as the secret and making the payload include a room name ("r"), the current time ("iat"), and the domain_id ("d") like:

{ "r": "test", "iat": 1610596413, "d": "30f866c3-9123-452a-8723-ff58322d09c5"}

Note: The domain_id is available from the domain configuration endpoint.

To learn more about, and test, your tokens please refer to https://jwt.io/.

Configuration properties in tokens use the following abbreviations:

Property	abbreviated
nbf	nbf
exp	exp
domain_id	d
room_name	r
user_id	ud
user_name	u
is_owner	o
knocking	k
close_tab_on_exit	ctoe
redirect_on_meeting_exit	rome
intercom_join_alert	ij
start_cloud_recording	sr
start_cloud_recording_opts	sro
auto_start_transcription	ast
enable_recording	er
enable_screenshare	ss
start_video_off	vo
start_audio_off	ao
meeting_join_hook	mjh
eject_at_token_exp	ejt
eject_after_elapsed	eje
lang	uil
enable_recording_ui	erui
permissions	p
The permissions property in tokens uses the following abbreviations:

JavaScript
Copy to clipboard
{
  // permissions - all fields optional
  "p": {
    // hasPresence
    "hp" : boolean,
    // canSend
    "cs": boolean | // shorthand meaning "all" or "none"
          // A string with some or all of the following values, separated by commas:
          // "v" -> "video"
          // "a" -> "audio"
          // "sv" -> "screenVideo"
          // "sa" -> "screenAudio"
          "v,a,sv,sa"
    // canReceive
    "cr": {
      // base
      "b": boolean | // shorthand meaning "all" or "none"
          {
            "v": false,  // video
            "a": true,   // audio
            "sv": false, // screenVideo
            "sa": true,  // screenAudio
            "cv": {      // customVideo
              "*": false
            },
            "ca": {      // customAudio
              "*": true
            }
          },
      // byUserId
      "u": {
        "foo": boolean | { /* ... */ } // same values as base
        // more user_ids here, or "*" for "all user_ids"
      },
      // byParticipantId
      "p": {
        "42fb115a-6d42-4155-ae4f-c96629f5217d": boolean | { /* ... */ } // same values as base
        // more participant ids here, or "*" for "all participant ids"
      }
    },
    // canAdmin
    "ca": boolean | // shorthand meaning "all" or "none"
          // A string with some or all of the following values, separated by commas:
          // "p" -> "participants"
          // "s" -> "streaming"
          // "t" -> "transcription"
          "p,s,t"
  }
}
POST
/meeting-tokens

A POST request to /meeting-tokens creates a new meeting token.

If the token is successfully created, a response body with a single field, token, is returned. Otherwise, an HTTP error is returned.

This is not the only way to generate a token. You can also self-sign the JWT using your API key. Read more here.
Body params

properties

room_name
string
The room for which this token is valid. If room_name isn't set, the token is valid for all rooms in your domain. *You should always set room_name if you are using this token to control access to a meeting.
eject_at_token_exp
boolean
Kick this user out of the meeting at the time this meeting token expires. If either this property or eject_after_elapsed are set for the token, the room's eject properties are overridden.

See an example in our advanced security tutorial.
Default: false
eject_after_elapsed
integer
Kick this user out of the meeting this many seconds after they join the meeting. If either this property or eject_at_token_exp are set for the token, the room's eject properties are overridden.

See an example in our advanced security tutorial.
nbf
integer
"Not before". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting in with this token before this time.
exp
integer
"Expires". This is a unix timestamp (seconds since the epoch.) Users cannot join a meeting with this token after this time.

Daily strongly recommends adding an exp value to all meeting tokens. Learn more in our Daily blog post: Add advanced security to video chats with the Daily API
is_owner
boolean
The user has meeting owner privileges. For example, if the room is configured for owner_only_broadcast and used in a Daily Prebuilt call, this user can send video, and audio, and can screenshare.
Default: false
user_name
string
The user's name in this meeting. The name displays in the user interface when the user is muted or has turned off the camera, and in the chat window. This username is also saved in the meeting events log (meeting events are retrievable using the analytics API methods.)
user_id
string
The user's ID for this meeting session. During a session, this ID is retrievable in the participants() method and related participant events. Either during or after a session concludes, this ID is retrievable using the /meetings REST API endpoint. You can use user_id to map between your user database and meeting events/attendance.

For domains configured for HIPAA compliance, if the user_id value is a UUID (for example, f81d4fae-7dec-11d0-a765-00a0c91e6bf6), then the UUID will be returned for the participant in the /meetings REST API endpoint. Otherwise, the string hipaa will be returned in order to remove potential PHI. During a session, the provided user_id will always be returned through the participants() method and related events, regardless of the user_id value.

The user_id has a limit of 36 characters.
enable_screenshare
boolean
Sets whether or not the user is allowed to screen share. This setting applies for the duration of the meeting. If you're looking to dynamically control whether a user can screen share during a meeting, then use the permissions token property.
Default: true
start_video_off
boolean
Disable the default behavior of automatically turning on a participant's camera on a direct join() (i.e. without startCamera() first).
Default: false
start_audio_off
boolean
Disable the default behavior of automatically turning on a participant's microphone on a direct join() (i.e. without startCamera() first).
Default: false
enable_recording
string
Jump to recording docs.
Options: "cloud","local","raw-tracks"
enable_prejoin_ui
boolean
Determines whether the participant using the meeting token enters a waiting room with a camera, mic, and browser check before joining a call. If this property is also set in the room or domain's configuration, the meeting token's configuration will take priority.

⚠️ You must be using Daily Prebuilt to use enable_prejoin_ui.
enable_live_captions_ui
boolean
Sets whether the participant sees a closed captions button in their Daily Prebuilt call tray. When the closed caption button is clicked, closed captions are displayed locally.

When set to true, a closed captions button appears in the call tray. When set to false, the closed captions button is hidden from the call tray.

Note: Transcription must be enabled for the room or users must have permission to start transcription for this feature to be enabled. View the transcription guide for more details.

⚠️ You must be using Daily Prebuilt to use enable_live_captions_ui.
enable_recording_ui
boolean
Determines whether the participant using the meeting token can see the Recording button in Daily Prebuilt's UI, which can be found in the video call tray. If this value is false, the button will not be included in the tray. If it's true, the Recording button will be displayed.

This option is useful when only specific call participants should have recording permissions.

⚠️ You must be using Daily Prebuilt to use enable_recording_ui.
enable_terse_logging
boolean
Reduces the volume of log messages. This feature should be enabled when there are more than 200 participants in a meeting to help improve performance.

See our guides for supporting large experiences for additional instruction.
Default: false
knocking
boolean
Requires the enable_knocking property to be set on the room. By default, if a user joins a room with enable_knocking set, and with a token, they will bypass the waiting screen and join the room directly. If this property is set to true, the user will be required to request access, and the owner will need to accept them before they can join.
Default: false
start_cloud_recording
boolean
PAY-AS-YOU-GO
Start cloud recording when the user joins the room. This can be used to always record and archive meetings, for example in a customer support context.

Note: This requires the enable_recording property of the room or token to be set to cloud. If you want to automatically record calls with other recording modes, use callObject.startRecording() after await callObject.join() in your code.
Default: false
start_cloud_recording_opts
object
PAY-AS-YOU-GO
Options for use when start_cloud_recording is true. See startRecording for available options.

⚠️ Specifying too many options may cause the token size to be very large. It is recommended to use token less than 2048 characters. For complex usecases, use the daily-js API.
auto_start_transcription
boolean
PAY-AS-YOU-GO
Start transcription when an owner joins the room. This property can be used to always transcribe meetings once an owner joins.
Default: false
close_tab_on_exit
boolean
(For meetings that open in a separate browser tab.) When a user leaves a meeting using the button in the in-call menu bar, the browser tab closes. This can be a good way, especially on mobile, for users to be returned to a previous website flow after a call.
Default: false
redirect_on_meeting_exit
string
(For meetings that open in a separate browser tab.) When a user leaves a meeting using the button in the in-call menu bar, the browser loads this URL. A query string that includes a parameter of the form recent-call=<domain>/<room> is appended to the URL. On mobile, you can redirect to a deep link to bring a user back into your app.
lang
string
The default language of the Daily prebuilt video call UI, for this room.

Setting the language at the token level will override any room or domain-level language settings you have.

Read more about changing prebuilt UI language settings.

* Norwegian "no" and Russian "ru" are only available in the new Daily Prebuilt.
Options: "da","de","en","es","fi","fr","it","jp","ka","nl","no","pt","pt-BR","pl","ru","sv","tr","user"
Default: en
permissions
object
Specifies the initial default permissions for a non-meeting-owner participant joining a call.

Each permission (i.e. each of the properties listed below) can be configured in the meeting token, the room, and/or the domain, in decreasing order of precedence.

Participant admins (those with the 'participants' value in their canAdmin permission) can also change participants' permissions on the fly during a call using updateParticipant() or updateParticipants().
hasPresence
boolean
Whether the participant appears as "present" in the call, i.e. whether they appear in participants().
canSend
boolean | array
Which types of media a participant should be permitted to send.

Can be:

An Array containing any of 'video', 'audio', 'screenVideo', and 'screenAudio'
true (meaning "all")
false (meaning "none")
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
boolean | array
Which admin tasks a participant is permitted to do.

Can be:

An array containing any of 'participants', 'streaming', or 'transcription'
true (meaning "all")
false (meaning "none")
Example requests

Create a token that grants access to a private room


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_KEY" \
     -XPOST -d \
     '{"properties":{"room_name":"room-0253"}}' \
     https://api.daily.co/v1/meeting-tokens
        
Create a token that configures screen sharing and recording

Here's how you might create a token that you use only for UI configuration with public rooms, not access control. This token enables screensharing, and recording, and could be used to give an "admin" user those features when joining a room that has them disabled by default. Notice that we don't set the room_name, so this token is valid for any room on your domain.


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_KEY" \
     -XPOST -d '{"properties":
                  {"enable_screenshare":true,
                   "enable_recording":"local"}}' \
     https://api.daily.co/v1/meeting-tokens

GET
/meeting-tokens/:meeting_token

A GET request to /meeting-tokens/:meeting_token validates a meeting token.

You can only validate tokens created for your domain.

If the token does not belong to your domain, or has an exp in the past, this endpoint will return an error.

If the token is currently valid and it belongs to your domain, this method returns an object that lists the token's properties.

If the token is not yet valid but will be in the future, meaning it has an nbf property, set the ignoreNbf query param to true to validate it.

Path params

meeting_token
string
Query params

ignoreNbf
boolean
Ignore the nbf in a JWT, if given
Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_KEY" \
     https://api.daily.co/v1/meeting-tokens/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE1NDg3MjE1NjksImV4cCI6MTg2NDA4MTUzOCwiciI6ImhlbGxvIiwibyI6dHJ1ZSwic3MiOnRydWUsImVyIjoibG9jYWwiLCJkIjoiMjVkZjUwNTctZWYwZC00ZDk3LWJkZTYtMGNmMjg3Mjc2Y2JiIiwiaWF0IjoxNTQ4NzIxODMxfQ.mvVciAengBR4xCblhFpo4mKYftQv1skYO4Y6IKr9Zgo

Logs
You can access call logs and metrics for every call to help you better understand your calls and troubleshoot issues as they arise.

Call logs characterize what happens on a call from the point of view of each participant. These logs include information about resource bundle downloads, signaling connections, peer-to-peer & SFU call connections and events, and participants' environments, actions, and error states.

Call metrics help to assess the performance and stability of the connection by providing transport layer, candidate-pair, and track level statistics.

Data starts being collected by the browser client once a second participant joins a call. The first data sample is logged after 15 seconds. Subsequent samples are logged every 15 seconds.

Accessing information

Call logs and metrics are made available through the Daily Dashboard and the /logs endpoint.

Additionally, we've built a sample app — Daily Call Explorer — as an example of how this information can be used.

Configuration
includeLogs
boolean
If true, you get a "logs" array in the results
Default: true
includeMetrics
boolean
If true, results have "metrics" array
Default: false
userSessionId
string
Filters by this user ID (aka "participant ID"). Required if mtgSessionId is not present in the request
mtgSessionId
string
Filters by this Session ID. Required if userSessionId is not present in the request
logLevel
string
Filters by the given log level name
Options: "ERROR","INFO","DEBUG"
order
string
ASC or DESC, case insensitive
Default: DESC
startTime
integer
A JS timestamp (ms since epoch in UTC)
endTime
integer
A JS timestamp (ms since epoch), defaults to the current time
limit
integer
Limit the number of logs and/or metrics returned
Default: 20
offset
integer
Number of records to skip before returning results
Default: 0

GET
/logs

A GET request to /logs returns a list of logs filtered by the provided query paramaters.

Query params

includeLogs
boolean
If true, you get a "logs" array in the results
Default: true
includeMetrics
boolean
If true, results have "metrics" array
Default: false
userSessionId
string
Filters by this user ID (aka "participant ID"). Required if mtgSessionId is not present in the request
mtgSessionId
string
Filters by this Session ID. Required if userSessionId is not present in the request
logLevel
string
Filters by the given log level name
Options: "ERROR","INFO","DEBUG"
order
string
ASC or DESC, case insensitive
Default: DESC
startTime
integer
A JS timestamp (ms since epoch in UTC)
endTime
integer
A JS timestamp (ms since epoch), defaults to the current time
limit
integer
Limit the number of logs and/or metrics returned
Default: 20
offset
integer
Number of records to skip before returning results
Default: 0
Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl --request GET \
  --header "Authorization: Bearer $API_KEY" \
  --url 'https://api.daily.co/v1/logs?mtgSessionId=7a99abff-0047-4b27-c6c1-49b4ec46f1de&userSessionId=4fde3659-71f6-4c28-9a90-e4c3f08ca611&includeMetrics=true'

GET
/logs/api

A GET request to /logs/api returns a list of REST API logs.

Query params

starting_after
string
Given the log ID, will return all records after that ID. See pagination docs
ending_before
string
Given the log ID, will return all records before that ID. See pagination docs
limit
integer
Limit the number of logs and/or metrics returned
Default: 20
source
string
The source of the given logs, either "api" or "webhook"
Default: "api"
url
string
Either the webhook server URL, or the API endpoint that was logged
Response Body Parameters

id
string
An ID identifying the log that was generated.
userId
string
The user ID associated with the owner of the account.
domainId
string
The domain ID associated with this log statement.
source
string
The source of this log statement. This will be "api" or "webhook".
ip
string
The originating IP address of this request.
method
string
The HTTP method used for this request.
url
string
The API route that was queried.
status
string
The HTTP status code returned by the endpoint.
createdAt
string
The timestamp representing when the record was created.
request
string
A JSON string representing the request body of this API request.
response
string
A JSON string representing the response body of this API request.
Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl --request GET \
  --header 'authorization: Bearer $API_KEY' \
  --url 'https://api.daily.co/v1/logs/api'

Meetings
The "meeting" object

JSON
Copy to clipboard
{
  "id": "82b92a0b-52cf-4495-f1bf-4d58a98a99b7",
  "room": "room-3",
  "start_time": 1549391714,
  "duration": 1650,
  "ongoing": true,
  "max_participants": 2,
  "participants": [
    {
      "user_id": null,
      "user_name": null,
      "participant_id": "11111111-2222-3333-4444-555555555555",
      "join_time": 1549391690,
      "duration": 1626
    },
    {
      "user_id": null,
      "user_name": null,
      "participant_id": "66666666-7777-8888-9999-000000000000",
      "join_time": 1549391714,
      "duration": 1650
    }
  ]
}
A meeting session is a set of one or more people in a room together during a specific time window.

Meeting session objects contain information about who joined calls in your rooms, when, and for how long.

Each meeting session object has six fields:

A unique, opaque meeting session id
The name of the room
A start_time (when the first user joined the session)
A duration
An ongoing boolean (true, if any participants are currently in the room)
A max_participants value (number), for the maximum number of participants that were present in the meeting at one time
A list of meeting session participants
The objects in the participants list five fields: join_time, duration, participant_id, user_id, and user_name. join_time, duration, and participant_id will always contain valid data. user_id and user_name fields will be null if that information is not available for the participant.

The start_time and join_time fields are unix timestamps (seconds since the epoch), and have approximately 15-second granularity. (We generally do not write a "meeting join" record until a user has stayed in a room for at least 10 seconds. ) The duration fields are elapsed times in seconds.

Because rooms are often reused, the definition of a meeting session needs to account for what happens when people join and leave rooms in arbitrary sequences. Here are the rules that determine the start and end bounds of a meeting session: A new meeting session begins when:

A single participant joins the room and has been alone for 30 seconds.
A second participant joins the room prior to the 30 seconds.
A participant remains in a room alone for 10 minutes after all others have left
A meeting session ends when:

All users leave the room. (The participant count is zero)
A participant remains in a room alone for 10 minutes after all others have left. (The participant count decrements to 1 for 10 minutes)
The intent of 10 minute reset is to try to match users expectations about what a "meeting" is. Some of our users leave rooms open for long periods of time, and stay in that room, and then are periodically joined by other people for "meetings." Thus, a user's unbroken time in a room might span multiple meeting sessions.

cURL
Copy to clipboard
# Example: get information about the 5 most recent meetings in classroom-104
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer DAILY_API_KEY" \
     https://api.daily.co/v1/meetings?room=classroom-104&limit=5
GET
/meetings

A GET request to /meetings returns a list of meeting sessions.

Meeting sessions are returned sorted by start_time time in reverse chronological order.

Results can be filtered by supplying any of room, timeframe_start, and timeframe_end arguments.

Each call to this endpoint fetches a maximum of 100 meeting session objects.

See Nuts and Bolts: Pagination for how pagination works in API requests (and how to use the limit, ending_before, and starting_after query parameters).
The response body consists of two fields: total_count and data.

The total_count field is the total number of meeting session objects that match the query, including the filtering by room, timeframe_start, and timeframe_end, but ignoring pagination arguments. (In other words, if pagination arguments are supplied, total_count could be greater than the number of meeting session objects returned by this query).

The data field is a list of meeting session objects. Each meeting session object includes the id, room (room name), start_time, duration (in seconds), a boolean that describes whether the meeting is ongoing, and a participants object of all meeting attendees.

Granularity of timestamps
The start_time, join_time, and duration fields are accurate to approximately 15 seconds. We don't write a "meeting join" record into our database until a user has stayed in a room for at least 10 seconds.
In general, we try to slightly undercount usage, to make sure we're not overcharging you for meeting participant-minutes!
Query params

room
string
timeframe_start
integer
timeframe_end
integer
limit
integer
starting_after
string
ending_before
string
ongoing
boolean
no_participants
boolean
The optional room argument should be a room name, and limits results to that room.

The optional timeframe_start argument is a unix timestamp, and limits results to meeting sessions that have a start_time greater than or equal to timeframe_start.

The optional timeframe_end argument is a unix timestamp, and limits results to meeting sessions that have a start_time less than timeframe_end.

The optional ongoing argument is a boolean value. If set to true, it limits results to meetings where participants are currently in the room. If set to false, it limits the results to meetings where there are no participants remaining in the room.

The optional no_participants argument is a boolean value. If set to true, this endpoint won't return the participant list in each meeting. This is useful for meetings with large numbers of participants. You can use the meetings/:meeting/participants endpoint to retrieve a paginated list of participants for a given meeting.

Example request

Get meeting sessions for a specific room and time frame


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer DAILY_API_KEY" \
     'https://api.daily.co/v1/meetings?room=7si1ARFeIM2bL6i6EU1X&timeframe_start=1548790970&timeframe_end=1548890974'
GET
/meetings/:meeting

A GET request to /meetings/:meeting returns information about the specified meeting session.

Path params

meeting
the ID of the meeting session
Example request

Get a meeting session


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer DAILY_API_KEY" \
     'https://api.daily.co/v1/meetings/71f3761e-3ce7-442a-88ed-78b0d61966b5'
GET
/meetings/:meeting/participants

A GET request to /meetings/:meeting/participants returns information about participants in the specified meeting session.

In order to paginate, you can use the joined_after field using the last participant id in the list. Once there are no more users remaining, you'll receive a 404 from the endpoint.

Path params

meeting
the ID of the meeting session
Query params

limit
the largest number of participant records to return
joined_after
limit to participants who joined after the given participant, identified by participant_id
joined_before
limit to participants who joined before the given participant, identified by participant_id
Example request

Get a meeting session


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer DAILY_API_KEY" \
     'https://api.daily.co/v1/meetings/71f3761e-3ce7-442a-88ed-78b0d61966b5/participants'
Presence
This endpoint provides near-real-time participant presence data[0].

/presence accepts no options and quickly returns all active participants the requestor can see, grouped by room.

/presence vs /meetings vs /logs
Please use this endpoint (not /meetings) if you need to know the current state of rooms and participants. If you need more in-depth analytics please see Meeting Analytics or Logs.
The "presence" object

JSON
Copy to clipboard
{
  "cool-room": [
    {
      "id": "4c8dee53-fd51-445c-92d4-917701401d14",
      "userId": "309cf686-64ba-4afa-9e6b-05fe13c56fbf",
      "userName": "sean",
      "joinTime": "2020-11-01T23:46:38.000Z",
      "duration": 543,
      "room": "cool-room"
    },
    ... more participants ...
  ]
}

Example request

cURL
Copy to clipboard
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer DAILY_API_KEY" \
     https://api.daily.co/v1/presence

Note: It should be sufficient to query this endpoint no more frequently than once every 15 seconds to get a complete picture of all of the participants on your domain.

[0] delay of up to 15 seconds.

GET
/presence

A GET request to /presence returns all active participants grouped by room.

Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_KEY" \
     https://api.daily.co/v1/presence

Phone numbers endpoint
PAY-AS-YOU-GO

You can do the following:

Search for available phone numbers to purchase
Purchase a phone number
Release a purchased phone number
List all the purchased phone numbers
There is no restriction on the number of phone numbers you can buy, however, a single phone number can send and receive hundreds of simultaneous calls.

Any purchased number can be used for PSTN dialout. However, a phone number can only be either used for Pinless Dialin or Pin Dialin. Read more details about SIP and PSTN in our guide.

CNAM Registration

Please contact help@daily.co for adding Caller Name (CNAM) to the purchased phone numbers. Daily will need your Name or Company Name to register with the United States CNAM Registry. Once registered, the Caller ID will display the appropriate name on the calling party's device.
GET
/list-available-numbers
PAY-AS-YOU-GO

List an available phone number

Query params

areacode
string
An areacode to search within.
region
string
A region or state to search within. Must be an ISO 3166-2 alpha-2 code, i.e. CA for California. Cannot be used in combination with areacode.
city
string
A specific City to search within. Example, New York. The string must be url encoded because it is a url parameter. Must be used in combination with region. Cannot be used in combination with areacode, starts_with, contains, or ends_with.
contains
string
A string of 3 to 7 digits that should appear somewhere in the number.
starts_with
string
A string of 3 to 7 digits that should be used as the start of a number. Cannot be used in combination with contains or ends_with.
ends_with
string
A string of 3 to 7 digits that should be used as the end of a number. Cannot be used in combination with starts_with or contains.
Example request


Request

200 OK

400 Validation Error

500 Vendor Unavailable
cURL
Copy to clipboard

curl  -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      https://api.daily.co/v1/list-available-numbers?region=CA&contains=vr000m

POST
/buy-phone-number

This will buy a phone number. In the POST request you can either provide the phone number you want to buy, or leave it empty. If the specified number is still available, it will be bought or the API will return a failure. Alternatively, if you skipped the number field, a random phone number from California (CA) will be bought.

You can check or find available numbers using the list-available-numbers API.

Body params

number
string
The phone number to purchase
Response Body

The response body contains two fields, an id and a number.

id: a UUID that uniquely identifies this phone-number. Will need this ID for deleting the phone-number
number: the purchased phone-number, for example, if a random was requested.
Example request


Request

200 OK
cURL
Copy to clipboard

curl --request POST \
  --url 'https://api.daily.co/v1/buy-phone-number' \
  --header 'Authorization: Bearer $TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
        "number": "+18058700061"
}'

DELETE
/release-phone-number/:id
PAY-AS-YOU-GO

A DELETE request to /release-phone-number/:id releases the the specified phone number referenced by its id.

A number cannot be deleted within the 14 days of purchase. Calling this API before this period expires results in an error.

Path params

id
string
Example request


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -XDELETE \
  https://api.daily.co/v1/release-phone-number/0cb313e1-211f-4be0-833d-8c7305b19902

GET
/purchased-phone-numbers
PAY-AS-YOU-GO

List the purchased phone numbers for this domain.

Each call to this endpoint fetches a maximum of 50 recording objects.

See our pagination reference for how pagination works in API requests (and how to use the limit, ending_before, and starting_after query parameters).
The response body consists of two fields: total_count and data.

The total_count field is the total number of phoneNumbers stored (which, if pagination arguments are supplied, could be greater than the number of phone numbers returned by this query).

The response message has a pagination_id field, which should be used for the pagination in the starting_after and ending_before

The data field is a list of phoneNumber objects.

Query params

limit
int32
ending_before
string
starting_after
string
filter_name
string
filter_number
string
Example request


Request

200 OK
cURL
Copy to clipboard

curl --request GET \
  --url 'https://api.daily.co/v1/purchased-phone-numbers' \
  --header 'Authorization: Bearer $TOKEN'
Listen for webhooks
Add a credit card to your account to unlock access to webhooks.
Webhooks are a helpful way to receive notifications about events that are occuring in Daily. In order to use webhooks, you'll need to create a web server with an endpoint that Daily can POST requests to as they occur. This allows you to track events in a more asynchronous and real-time fashion, instead of polling with API requests.

Available webhook endpoints

Create a webhook
Delete a webhook
Get webhooks
Get webhook info
Update a webhook
Configuring Webhooks

In order to configure a webhook, you'll need to create a HTTP server. You can use an online service like webhook.site for testing, or test locally using a a service like ngrok.

When an asynchronous event occurs, we'll send a POST request to an endpoint you provide containing a request body that details the event. Once you have a server set up with an accompanying endpoint, you can send that to the POST /webhooks endpoint to create a webhook. Webhook events are sent for all rooms on your domain.

cURL
Copy to clipboard
curl --location --request POST 'https://daily.co/api/v1/webhooks' \
--header 'Authorization: Bearer $TOKEN' \
--header 'Content-Type: text/plain' \
--data-raw '{
    "url": "$WEBHOOK_URL",
    "eventTypes": ["recording.started", "recording.ready-to-download"]
}'

Before creating your webhook, we perform a verification check to ensure your endpoint is active and capable of handling webhook events.

We'll send a POST request to your webhook endpoint with the following payload:

JSON
Copy to clipboard
{
  "test": "test"
}
If your endpoint returns a 200 status code, we will proceed to create your webhook. The response to the initial creation request will include details of the newly created webhook, such as its ID and event subscriptions.

JSON
Copy to clipboard
{
  "uuid": "0b4e4c7c-5eaf-46fe-990b-a3752f5684f5",
  "url": "$WEBHOOK_URL",
  "hmac": "NQrSA5z0FkJ44QPrFerW7uCc5kdNLv3l2FDEKDanL1U=",
  "eventTypes": [
    "recording.started",
    "recording.ready-to-download"
  ],
  "state": "ACTIVE",
  "failedCount": 0,
  "domainId": "$DOMAIN_ID",
  "createdAt": "2023-08-15T18:28:30.317Z",
  "updatedAt": "2023-08-15T18:28:30.317Z"
}
When creating a webhook via the POST /webhooks endpoint, Daily will send a request to the webhook server with a test request body. If we do not receive a 200 status code relatively quickly, we will consider the endpoint faulty and return a 400 error. It can be helpful to return a response immediately before handling the event to avoid webhook disruptions.
The webhooks service will return an hmac secret that you can use to verify the signature of a webhook. You may also pass in an hmac during a create or update request, if you'd like to specify your own secret. This secret must be BASE-64 encoded.
At this point, you can use the uuid field and the GET /webhooks/:uuid endpoint to receive information about your webhook.

cURL
Copy to clipboard
curl --location --request GET 'https://daily.co/api/v1/webhooks/0b4e4c7c-5eaf-46fe-990b-a3752f5684f5' \
--header 'Authorization: Bearer $TOKEN'

JSON
Copy to clipboard
{
  "uuid": "0b4e4c7c-5eaf-46fe-990b-a3752f5684f5",
  "url": "$WEBHOOK_URL",
  "hmac": "NQrSA5z0FkJ44QPrFerW7uCc5kdNLv3l2FDEKDanL1U=",
  "basicAuth": null,
  "eventTypes": [
    "recording.started",
    "recording.ready-to-download"
  ],
  "state": "ACTIVE",
  "failedCount": 0,
  "lastMomentPushed": "2023-08-15T18:29:52.000Z",
  "domainId": "$DOMAIN_ID",
  "createdAt": "2023-08-15T18:28:30.000Z",
  "updatedAt": "2023-08-15T18:29:52.000Z"
}
Webhook Structure

state

Webhooks have a state field that may either be "FAILED" or "ACTIVE".

Your webhook may enter the FAILED state if we fail to send an event to your webhook server 3 times. Succesful attempts will reset this counter. We require your webhook server to send a 200 status code relateively quickly, so be sure to respond to the request as soon as you receive it. See retryType for an alternative error handling behavior.

If your webhook has entered a failed state, we will no longer send events to that webhook. You can re-activate a webhook by sending a POST request to /webhooks/:uuid, where uuid is your webhook uuid. This will once again send a test message to the endpoint provided, and if a 200 is returned, we will re-activate the webhook.

You may also update the other webhook fields such as eventTypes if needed with this endpoint.

hmac

The hmac field contains a secret that is shared between Daily and you. Ensure that you do not share this secret publicly, otherwise you will not be able to verify that an event came from Daily.
Webhooks provide an hmac, which is a BASE-64 encoded HMAC-sha256 secret that allows you to verify that the event in question actually came from Daily. You may also provide your own secret when creating a webhook, as long as it is BASE-64 encoded. When POSTing to your webhook server, Daily will provide two headers: X-Webhook-Signature and X-Webhook-Timestamp.

In order to verify the signature yourself, you'll need to compute the signature in a manner provided in the snippet below:

JavaScript
Copy to clipboard
// You'll need to save the hmac value the API returned when you created your webhook and insert it here
let hmacSecret = 'NQrSA5z0FkJ44QPrFerW7uCc5kdNLv3l2FDEKDanL1U=';
let signature = headers['X-Webhook-Timestamp'] + '.' + JSON.stringify(event);
const base64DecodedSecret = Buffer.from(hmacSecret, 'base64');
const hmac = crypto.createHmac('sha256', base64DecodedSecret);
let computed_signature = hmac.update(signature).digest('base64');
expect(computed_signature).toStrictEqual(headers['X-Webhook-Signature']);

event is the response body from the event that was POSTed to your webhook server. From there, you can sign the content with the HMAC-sha256 string, and ensure that your signature matches the one in the X-Webhook-Signature header. As only Daily and you hold the hmac, this comparison ensures that the request came from Daily.

failedCount

This is incremented every time Daily fails to send an event to the given webhook endpoint. This can happen if your server is not responding quickly enough or if it is returning a non-200 status code. When this happens 3 times, the webhook will enter the FAILED state. If we have a succesful response at any time before this we will reset your failedCount to 0. Thus, intermittent failures should not cause the circuit breaker to flip.

basicAuth

You may provide a basicAuth field when creating a webhook if you'd like Daily to send an Authorization header with a Basic {secret} value. This can be checked by your endpoint and used as an additional shared secret to ensure that you are only processing verified events from Daily.

retryType

There are currently two retry type configurations available. circuit-breaker is the default. You can pass this field when creating a webhook, or updating a webhook.

circuit-breaker

This is the default retry type. Every message is treated equally, and is tried at least once. Each failure to your webhook server is counted, and if it ever reaches 3 failures or greater, a circuit breaker is flipped. At this point, Daily will stop attempting to send webhooks to the server. You can close the circuit breaker by sending a POST request to /webhooks/:uuid, which will attempt to send a request to your server again. If your server resolves correctly, Daily will begin sending events.

exponential

This retry is message based, instead of the global count that circuit-breaker uses. While failedCount is still incremented, Daily will never circuit break under this retry type. Each message will be retried at most 5 times, with an exponential backoff up to 15 minutes. If a message fails being sent 5 times, it will be deleted and no longer retried.

Webhook Events

We provide several webhook events that you can subscribe to. See the webhook events index for more details.

meeting.started
meeting.ended
participant.joined
participant.left
waiting-participant.joined
waiting-participant.left
recording.started
recording.ready-to-download
recording.error
transcript.started
transcript.ready-to-download
transcript.error
streaming.started
streaming.updated
streaming.ended
streaming.error
batch-processor.job-finished
batch-processor.error
dialout.connected
dialout.answered
dialout.stopped
dialout.warning
dialout.error
dialin.ready
dialin.connected
dialin.stopped
dialin.warning
dialin.error

Webhook Events
PAY-AS-YOU-GO
Head to our webhooks page for detailed information on using webhooks.
We provide several webhook events that you can subscribe to.

meeting.started
meeting.ended
participant.joined
participant.left
waiting-participant.joined
waiting-participant.left
recording.started
recording.ready-to-download
recording.error
transcript.started
transcript.ready-to-download
transcript.error
streaming.started
streaming.updated
streaming.ended
streaming.error
batch-processor.job-finished
batch-processor.error
dialout.connected
dialout.answered
dialout.stopped
dialout.warning
dialout.error
dialin.ready
dialin.connected
dialin.stopped
dialin.warning
dialin.error

Meeting Started
A meeting started event emits when Daily begins a call. This occurs when a participant first joins a room.

Webhook Events

There are five common fields all events share:

version
string
Represents the version of the event. This uses semantic versioning to inform a consumer if the payload has introduced any breaking changes.
type
string
Represents the type of the event described in the payload.
id
string
An identifier representing this specific event.
payload
object
An object representing the event, whose fields are described below.
event_ts
number
Documenting when the webhook itself was sent. This timestamp is different than the time of the event the webhook describes. For example, a recording.started event will contain a start_ts timestamp of when the actual recording started, and a slightly later event_ts timestamp indicating when the webhook event was sent.
Payload

version
string
The semantic version of the current message.
type
string
The type of event that is being provided.
Options: "meeting.started"
event_ts
number
The Unix epoch time in seconds representing when the event was generated.
payload
object
The payload of the object, describing the given event.
start_ts
number
The Unix epoch time in seconds representing when meeting started.
meeting_id
string
The meeting ID.
room
string
The name of the room.
JSON
Copy to clipboard
{
  "version": "1.0.0",
  "type": "meeting.started",
  "id": "met-sta-f2aa1ade-ff80-464c-b46e-50ffa577d48d-1708526032",
  "payload": {
    "start_ts": 1708526032.672,
    "meeting_id": "f2aa1ade-ff80-464c-b46e-50ffa577d48d",
    "room": "TrPmUX1DzjSwDaAFDfNj"
  },
  "event_ts": 1708526033.049
}
Meeting Ended
A meeting ended event is emitted when the last participant in a call leaves. There can be a delay up to 20 seconds to determine if the meeting has ended, permitting reconnections, before sending the event.

Webhook Events

There are five common fields all events share:

version
string
Represents the version of the event. This uses semantic versioning to inform a consumer if the payload has introduced any breaking changes.
type
string
Represents the type of the event described in the payload.
id
string
An identifier representing this specific event.
payload
object
An object representing the event, whose fields are described below.
event_ts
number
Documenting when the webhook itself was sent. This timestamp is different than the time of the event the webhook describes. For example, a recording.started event will contain a start_ts timestamp of when the actual recording started, and a slightly later event_ts timestamp indicating when the webhook event was sent.
Payload

version
string
The semantic version of the current message.
type
string
The type of event that is being provided.
Options: "meeting.ended"
event_ts
number
The Unix epoch time in seconds representing when the event was generated.
payload
object
The payload of the object, describing the given event.
start_ts
number
The Unix epoch time in seconds representing when the meeting started.
end_ts
number
The Unix epoch time in seconds representing when the meeting ended.
meeting_id
string
The meeting ID.
room
string
The name of the room.
JSON
Copy to clipboard
{
  "version": "1.0.0",
  "type": "meeting.ended",
  "id": "met-end-f2aa1ade-ff80-464c-b46e-50ffa577d48d-1708526104",
  "payload": {
    "start_ts": 1708526032,
    "end_ts": 1708526104.671,
    "meeting_id": "f2aa1ade-ff80-464c-b46e-50ffa577d48d",
    "room": "TrPmUX1DzjSwDaAFDfNj"
  },
  "event_ts": 1708526125.197
}

Participant Joined
A participant joined event is sent when a participant joins a meeting.

Webhook Events

There are five common fields all events share:

version
string
Represents the version of the event. This uses semantic versioning to inform a consumer if the payload has introduced any breaking changes.
type
string
Represents the type of the event described in the payload.
id
string
An identifier representing this specific event.
payload
object
An object representing the event, whose fields are described below.
event_ts
number
Documenting when the webhook itself was sent. This timestamp is different than the time of the event the webhook describes. For example, a recording.started event will contain a start_ts timestamp of when the actual recording started, and a slightly later event_ts timestamp indicating when the webhook event was sent.
Payload

version
string
The semantic version of the current message.
type
string
The type of event that is being provided.
Options: "participant.joined"
event_ts
number
The Unix epoch time in seconds representing when the event was generated.
payload
object
The payload of the object, describing the given event.
joined_at
number
The Unix epoch time in seconds representing when the participant joined.
session_id
string
The user session ID, or participant id.
room
string
The name of the room.
user_id
string
The ID of the user, set by the meeting token.
user_name
string
The name of the user, set by the meeting token.
owner
boolean
A flag determining if this user is considered the owner.
networkQualityState
string
The quality of the user's network.
Options: "unknown","good","warning","bad"
will_eject_at
number
The Unix epoch time in seconds representing when the participant will be ejected.
permissions
object
The permissions object, that describes what the participant is permitted to do during this call.
hasPresence
boolean
Determines whether the participant is "present" or "hidden"
canSend
array
Array of strings identifying which types of media the participant can send or a boolean to grant/revoke permissions for all media types.
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
array
Array of strings identifying which types of admin tasks the participant can do or a boolean to grant/revoke permissions for all types.
JSON
Copy to clipboard
{
  "version": "1.0.0",
  "type": "participant.joined",
  "id": "ptcpt-join-6497c79b-f326-4942-aef8-c36a29140ad1-1708972279961",
  "payload": {
    "room": "test",
    "user_id": "6497c79b-f326-4942-aef8-c36a29140ad1",
    "user_name": "testuser",
    "session_id": "0c0d2dda-f21d-4cf9-ab56-86bf3c407ffa",
    "joined_at": 1708972279.96,
    "will_eject_at": 1708972299.541,
    "owner": false,
    "permissions": {
      "hasPresence": true,
      "canSend": true,
      "canReceive": {
        "base": true
      },
      "canAdmin": false
    }
  },
  "event_ts": 1708972279.961
}

Participant Left
A participant left event is sent when a participant leaves a meeting.

Webhook Events

There are five common fields all events share:

version
string
Represents the version of the event. This uses semantic versioning to inform a consumer if the payload has introduced any breaking changes.
type
string
Represents the type of the event described in the payload.
id
string
An identifier representing this specific event.
payload
object
An object representing the event, whose fields are described below.
event_ts
number
Documenting when the webhook itself was sent. This timestamp is different than the time of the event the webhook describes. For example, a recording.started event will contain a start_ts timestamp of when the actual recording started, and a slightly later event_ts timestamp indicating when the webhook event was sent.
Payload

version
string
The semantic version of the current message.
type
string
The type of event that is being provided.
Options: "participant.left"
event_ts
number
The Unix epoch time in seconds representing when the event was generated.
payload
object
The payload of the object, describing the given event.
joined_at
number
The Unix epoch time in seconds representing when the participant joined.
duration
number
The time in seconds representing how long the participant was in the call.
session_id
string
The user session ID, or participant id.
room
string
The name of the room.
user_id
string
The ID of the user, set by the meeting token.
user_name
string
The name of the user, set by the meeting token.
owner
boolean
A flag determining if this user is considered the owner.
networkQualityState
string
The quality of the user's network.
Options: "unknown","good","warning","bad"
will_eject_at
number
The Unix epoch time in seconds representing when the participant will be ejected.
permissions
object
The permissions object, that describes what the participant is permitted to do during this call.
hasPresence
boolean
Determines whether the participant is "present" or "hidden"
canSend
array
Array of strings identifying which types of media the participant can send or a boolean to grant/revoke permissions for all media types.
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
array
Array of strings identifying which types of admin tasks the participant can do or a boolean to grant/revoke permissions for all types.
JSON
Copy to clipboard
{
  "version": "1.0.0",
  "type": "participant.left",
  "id": "ptcpt-left-16168c97-f973-4eae-9642-020fe3fda5db-1708972302986",
  "payload": {
    "room": "test",
    "user_id": "16168c97-f973-4eae-9642-020fe3fda5db",
    "user_name": "bipol",
    "session_id": "0c0d2dda-f21d-4cf9-ab56-86bf3c407ffa",
    "joined_at": 1708972291.567,
    "will_eject_at": null,
    "owner": false,
    "permissions": {
      "hasPresence": true,
      "canSend": true,
      "canReceive": {
        "base": true
      },
      "canAdmin": false
    },
    "duration": 11.419000148773193
  },
  "event_ts": 1708972302.986
}

Waiting Participant Joined
A waiting participant joined event is sent when a knocker (see blog post) begins to knock. Once a waiting participant is allowed to join the call, a participant.joined event is sent. Otherwise, if a participant leaves the knocking state, a waiting-participant.left is sent.

Webhook Events

There are five common fields all events share:

version
string
Represents the version of the event. This uses semantic versioning to inform a consumer if the payload has introduced any breaking changes.
type
string
Represents the type of the event described in the payload.
id
string
An identifier representing this specific event.
payload
object
An object representing the event, whose fields are described below.
event_ts
number
Documenting when the webhook itself was sent. This timestamp is different than the time of the event the webhook describes. For example, a recording.started event will contain a start_ts timestamp of when the actual recording started, and a slightly later event_ts timestamp indicating when the webhook event was sent.
Payload

version
string
The semantic version of the current message.
type
string
The type of event that is being provided.
Options: "waiting-participant.joined"
event_ts
number
The Unix epoch time in seconds representing when the event was generated.
payload
object
The payload of the object, describing the given event.
joined_at
number
The Unix epoch time in seconds representing when the waiting participant joined.
session_id
string
The user session ID, or participant id.
room
string
The name of the room.
user_id
string
The ID of the user, set by the meeting token.
user_name
string
The name of the user, set by the meeting token.
owner
boolean
A flag determining if this user is considered the owner.
networkQualityState
string
The quality of the user's network.
Options: "unknown","good","warning","bad"
will_eject_at
integer
The Unix epoch time in seconds representing when the participant will be ejected.
permissions
object
The permissions object, that describes what the participant is permitted to do during this call.
hasPresence
boolean
Determines whether the participant is "present" or "hidden"
canSend
array
Array of strings identifying which types of media the participant can send or a boolean to grant/revoke permissions for all media types.
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
array
Array of strings identifying which types of admin tasks the participant can do or a boolean to grant/revoke permissions for all types.
JSON
Copy to clipboard
{
  "version": "1.0.0",
  "type": "waiting-participant.joined",
  "id": "1-w-ptcpt-joined-ed25c43f-e763-4f4d-acbd-51c399a616f1",
  "payload": {
    "room": "knocking",
    "user_name": "bipol",
    "session_id": "ed25c43f-e763-4f4d-acbd-51c399a616f1",
    "joined_at": 1719586645.076,
    "will_eject_at": null,
    "owner": false,
    "permissions": {
      "hasPresence": true,
      "canSend": true,
      "canReceive": {
        "base": true
      },
      "canAdmin": false
    },
    "duration": 0
  },
  "event_ts": 1719586645.077
}
;

Waiting Participant Left
A waiting participant left event is sent when a knocking participant (see blog post) leaves the knocking state. In other words, when a knocker begins to knock and leaves before being allowed into a room, a waiting-participant.left event is sent. If a knocker is allowed into a room and then leaves, a participant.left event is sent.

Webhook Events

There are five common fields all events share:

version
string
Represents the version of the event. This uses semantic versioning to inform a consumer if the payload has introduced any breaking changes.
type
string
Represents the type of the event described in the payload.
id
string
An identifier representing this specific event.
payload
object
An object representing the event, whose fields are described below.
event_ts
number
Documenting when the webhook itself was sent. This timestamp is different than the time of the event the webhook describes. For example, a recording.started event will contain a start_ts timestamp of when the actual recording started, and a slightly later event_ts timestamp indicating when the webhook event was sent.
Payload

version
string
The semantic version of the current message.
type
string
The type of event that is being provided.
Options: "waiting-participant.left"
event_ts
number
The Unix epoch time in seconds representing when the event was generated.
payload
object
The payload of the object, describing the given event.
joined_at
number
The Unix epoch time in seconds representing when the waiting participant joined.
duration
number
The time in seconds representing how long the participant was in the call.
session_id
string
The user session ID, or participant id.
room
string
The name of the room.
user_id
string
The ID of the user, set by the meeting token.
user_name
string
The name of the user, set by the meeting token.
owner
boolean
A flag determining if this user is considered the owner.
networkQualityState
string
The quality of the user's network.
Options: "unknown","good","warning","bad"
will_eject_at
integer
The Unix epoch time in seconds representing when the participant will be ejected.
permissions
object
The permissions object, that describes what the participant is permitted to do during this call.
hasPresence
boolean
Determines whether the participant is "present" or "hidden"
canSend
array
Array of strings identifying which types of media the participant can send or a boolean to grant/revoke permissions for all media types.
canReceive
object
Which media the participant should be permitted to receive.

See here for canReceive object format.
canAdmin
array
Array of strings identifying which types of admin tasks the participant can do or a boolean to grant/revoke permissions for all types.
JSON
Copy to clipboard
{
  "version": "1.0.0",
  "type": "waiting-participant.left",
  "id": "1-w-ptcpt-left-c85f48f3-82ec-4648-b39c-edfce7acf062",
  "payload": {
    "room": "knocking",
    "user_name": "bipol",
    "session_id": "c85f48f3-82ec-4648-b39c-edfce7acf062",
    "joined_at": 1719586614.027,
    "will_eject_at": null,
    "owner": false,
    "permissions": {
      "hasPresence": true,
      "canSend": true,
      "canReceive": {
        "base": true
      },
      "canAdmin": false
    },
    "duration": 14.403000116348267
  },
  "event_ts": 1719586628.431
}

Recording Started
A recording started event emits when Daily begins to record a call. These can be activated via startRecording(), via the REST API, or within Prebuilt.

Webhook Events

There are five common fields all events share:

version
string
Represents the version of the event. This uses semantic versioning to inform a consumer if the payload has introduced any breaking changes.
type
string
Represents the type of the event described in the payload.
id
string
An identifier representing this specific event.
payload
object
An object representing the event, whose fields are described below.
event_ts
number
Documenting when the webhook itself was sent. This timestamp is different than the time of the event the webhook describes. For example, a recording.started event will contain a start_ts timestamp of when the actual recording started, and a slightly later event_ts timestamp indicating when the webhook event was sent.
Payload

version
string
The semantic version of the current message.
type
string
The type of event that is being provided.
Options: "recording.started"
event_ts
number
The Unix epoch time in seconds representing when the event was generated.
payload
object
The payload of the object, describing the given event.
recording_id
string
An ID identifying the recording that was generated.
action
string
A string describing the event that was emitted.
Options: "start-cloud-recording"
layout
object
The layout used for the recording.
Default Layout

preset
string
Options: "default"
max_cam_streams
number
Single Participant Layout

preset
string
Options: "single-participant"
session_id
string
Active Participant Layout

preset
string
Options: "active-participant"
Portrait Layout

preset
string
Options: "portrait"
variant
string
Options: "vertical","inset"
max_cam_streams
number
Custom Layout

preset
string
Options: "custom"
composition_id
string
composition_params
object
session_assets
object
started_by
string
The participant ID of the user who started the recording.
instance_id
string
The recording instance ID that was passed into the start recording command.
start_ts
integer
The Unix epoch time in seconds representing when the recording started.
JSON
Copy to clipboard
{
  "version": "1.0.0",
  "type": "recording.started",
  "id": "rec-sta-c3df927c-f738-4471-a2b7-066fa7e95a6b-1692124183",
  "payload": {
    "action": "start-cloud-recording",
    "recording_id": "08fa0b24-9220-44c5-846c-3f116cf8e738",
    "layout": {
      "preset": "active-participant"
    },
    "started_by": "0a20567c-9e95-4fa7-aaa3-fb62f5be0449",
    "instance_id": "c3df927c-f738-4471-a2b7-066fa7e95a6b",
    "start_ts": 1692124183
  },
  "event_ts": 1692124183
}

POST
/webhooks
PAY-AS-YOU-GO

A POST request to /webhooks creates a new webhook.

Creates a new webhook. Returns an error if the webhook URL provided does not return a 200 status code within a few seconds. Upon creation, new sessions should begin to emit the events specified in the eventTypes field.

When creating a webhook via the POST /webhooks endpoint, Daily will send a request to the webhook server with a test request body. If we do not receive a 200 status code relatively quickly, we will consider the endpoint faulty and return a 400 error. It can be helpful to return a response immediately before handling the event to avoid webhook disruptions.
Body params

url
string
The webhook server endpoint that was provided.
basicAuth
string
The basic auth credentials that will be used to POST to the webhook URL.
retryType
string
The retry configuration for this webhook endpoint to use. The default is circuit-breaker.
Options: "circuit-breaker","exponential"
eventTypes
array
The set of event types this webhook is subscribed to.
hmac
string
A secret that can be used to verify the signature of the webhook. If not provided, an hmac will be provisioned for you and returned.
Response Body Parameters

uuid
string
The unique identifier for this webhook.
url
string
The webhook server endpoint that was provided.
hmac
string
A secret that can be used to verify the signature of the webhook.
basicAuth
string
The basic auth credentials that will be used to POST to the webhook URL.
retryType
string
The retry configuration for this webhook endpoint to use. The default is circuit-breaker.
Options: "circuit-breaker","exponential"
eventTypes
array
The set of event types this webhook is subscribed to.
state
string
The current state of the webhook. "FAILED" | "INACTIVE"
failedCount
number
The number of consecutive failures this webhook has made.
lastMomentPushed
string
The ISO 8601 time of the last moment an event was pushed to the webhook server.
domainId
string
The domain ID this webhook is associated with.
createdAt
string
The ISO 8601 time of when this webhook was created.
updatedAt
string
The ISO 8601 time of when this webhook was last updated.
Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl --location --request POST 'https://daily.co/api/v1/webhooks' --header 'Authorization: Bearer $TOKEN' --header 'Content-Type: text/plain' --data-raw '{
    "url": "$WEBHOOK_URL",
    "eventTypes": ["recording.started", "recording.ready-to-download"]
}'

POST
/webhooks/:uuid
PAY-AS-YOU-GO

A POST request to /webhooks/:uuid updates your webhook.

This endpoint allows you to update the given webhook. You can subscribe to new events or alter your url. You can also use this endpoint to re-activate a webhook that has entered a failed state - just use the same url as before, and Daily will verify that the endpoint is connectable and turn the webhook back on.

When updating a webhook via the POST /webhooks endpoint, Daily will send a request to the webhook server with a test request body. If we do not receive a 200 status code relatively quickly, we will consider the endpoint faulty and return a 400 error. It can be helpful to return a response immediately before handling the event to avoid webhook disruptions.
Path params

uuid
string
The uuid of the webhook.
Body params

url
string
The webhook server endpoint that was provided.
basicAuth
string
The basic auth credentials that will be used to POST to the webhook URL.
retryType
string
The retry configuration for this webhook endpoint to use. The default is circuit-breaker.
Options: "circuit-breaker","exponential"
eventTypes
array
The set of event types this webhook is subscribed to.
hmac
string
A secret that can be used to verify the signature of the webhook.
Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl --location --request POST 'https://api.daily.co/v1/webhooks' --header 'Authorization: Bearer $TOKEN' --header 'Content-Type: text/plain' --data-raw '{
    "url": "$WEBHOOK_URL",
    "eventTypes": ["recording.started", "recording.ready-to-download"]
}'

DELETE
/webhooks/:uuid
PAY-AS-YOU-GO

A DELETE request to /webhooks/:uuid deletes your webhook.

Deletes the given webhook. The webhook will immediately become inactive and no further events will be sent to the endpoint.

Path params

uuid
string
The uuid of the webhook.
Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl --location --request DELETE 'https://api.daily.co/v1/webhooks/$WEBHOOK_ID' --header 'Authorization: Bearer $TOKEN'

GET
/webhooks
PAY-AS-YOU-GO

A GET request to /webhooks returns your webhook.

Retrieve a list of webhooks. Currently, a domain may only have one webhook returned, so you may expect only one webhook in the returned array.

Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -XGET \
     https://api.daily.co/v1/webhooks

GET
/webhooks/:uuid
PAY-AS-YOU-GO

A GET request to /webhooks/:uuid returns your webhook.

Returns the webhook at the given uuid.

uuid
string
The uuid of the webhook.
Response Body Parameters

uuid
string
The unique identifier for this webhook.
url
string
The webhook server endpoint that was provided.
hmac
string
A secret that can be used to verify the signature of the webhook.
basicAuth
string
The basic auth credentials that will be used to POST to the webhook URL.
retryType
string
The retry configuration for this webhook endpoint to use. The default is circuit-breaker.
Options: "circuit-breaker","exponential"
eventTypes
array
The set of event types this webhook is subscribed to.
state
string
The current state of the webhook. "FAILED" | "INACTIVE"
failedCount
number
The number of consecutive failures this webhook has made.
lastMomentPushed
string
The ISO 8601 time of the last moment an event was pushed to the webhook server.
domainId
string
The domain ID this webhook is associated with.
createdAt
string
The ISO 8601 time of when this webhook was created.
updatedAt
string
The ISO 8601 time of when this webhook was last updated.
Example requests


Request

200 OK

400 bad request
cURL
Copy to clipboard

curl --location --request GET 'https://daily.co/api/v1/webhooks/$WEBHOOK_ID' --header 'Authorization: Bearer $TOKEN'

Daily Client SDK for Python
The Daily Client SDK for Python allows you to build video and audio calling into your native desktop and server applications.

Installation

For installation instructions, follow the Daily Python installation guide.

Guide

To learn more about building apps with the Daily Client SDK for Python, read our getting started guide.

Demo apps

To see working examples of how to interact with the Daily Client SDK for Python, see our public demo apps.

API Reference

For API reference and types information, check out our reference documentation.

Installing the Daily Client SDK for Python
Installing using pip

daily-python can be easily installed using pip:

pip install daily-python

To upgrade:

pip install -U daily-python

Requirements

Python 3.8 or newer