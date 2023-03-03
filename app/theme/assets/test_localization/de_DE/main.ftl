hello = Hallo {$name}!
time-elapsed = Time elapsed: { $duration }s.

emails =
    { $unreadEmails ->
        [one] Du hast eine neue, ungelesene Mail.
       *[other] Du hast { $unreadEmails } ungelesene eMails.
    }
