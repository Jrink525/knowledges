    # @kernel_function(description="安排一次会议")
    def schedule_meeting(
        self, title: str, attendees: str, datetime_str: str
    ) -> str:
        return f"Meeting '{title}' scheduled for {datetime_str}"


