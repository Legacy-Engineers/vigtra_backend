
        if data["status"] not in [status.value for status in ContributionPlanStatus]:
            valid_statuses = [status.value for status in ContributionPlanStatus]
            return vigtra_message(
                message="Error when creating contribution plan, status is invalid",
                data=data,
                error_details=[
                    "Error when creating contribution plan, status is invalid",
                    f"Valid statuses are: {valid_statuses}",
                ],
            )

        if (
            data["status"] == ContributionPlanStatus.ACTIVE
            and data["start_date"] is None
        ):
            return vigtra_message(
                message="Error when creating contribution plan, start_date is required when status is ACTIVE",
                data=data,
                error_details=[
                    "Error when creating contribution plan, start_date is required when status is ACTIVE"
                ],
            )

        if (
            data["status"] == ContributionPlanStatus.INACTIVE
            and data["end_date"] is None
        ):
            return vigtra_message(
                message="Error when creating contribution plan, end_date is required when status is INACTIVE",
                data=data,
                error_details=[
                    "Error when creating contribution plan, end_date is required when status is INACTIVE"
                ],
            )

        if (
            data["status"] == ContributionPlanStatus.INACTIVE
            and data["start_date"] is not None
        ):
            return vigtra_message(
                message="Error when creating contribution plan, start_date is not allowed when status is INACTIVE",
                data=data,
                error_details=[
                    "Error when creating contribution plan, start_date is not allowed when status is INACTIVE"
                ],
            )

        if (
            data["status"] == ContributionPlanStatus.ACTIVE
            and data["end_date"] is not None
        ):
            return vigtra_message(
                message="Error when creating contribution plan, end_date is not allowed when status is ACTIVE",
                data=data,
                error_details=[
                    "Error when creating contribution plan, end_date is not allowed when status is ACTIVE"
                ],
            )