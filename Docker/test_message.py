import synapseclient

syn = synapseclient.Synapse()

syn.sendMessage(
    userIds=[participantid],
    messageSubject=subject,
    messageBody="".join(message))
