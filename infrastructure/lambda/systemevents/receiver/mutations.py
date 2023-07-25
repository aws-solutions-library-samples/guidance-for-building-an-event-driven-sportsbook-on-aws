add_system_event = """
mutation MyMutation ($input: SystemEventInput!) {
  addSystemEvent(input: $input) {
    ... on SystemEvent {
      __typename
      source
      detailType
      detail
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""
