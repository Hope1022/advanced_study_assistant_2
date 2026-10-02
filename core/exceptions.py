from fastapi import HTTPException, status

InvalidTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token dead or expired",
    headers={"WWW-Authenticate": "Bearer"},
)


TokenTypeMismatchException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token mismatch",
    headers={"WWW-Authenticate": "Bearer"},
)

InvalidCredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid email or password",
    headers={"WWW-Authenticate": "Bearer"},
)

UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found.",
)

EmailAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="An account with this email already exists.",
)

InsufficientPermissionsException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have permission to perform this action.",
)
 
ResourceNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="The requested resource was not found.",
)

BadRequestException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid request.",
)


# AlreadyMemberException = HTTPException(
#     status_code=status.HTTP_409_CONFLICT,
#     detail="You are already a member of this group.",
# )

# GroupFullException = HTTPException(
#     status_code=status.HTTP_409_CONFLICT,
#     detail="This group has reached its maximum capacity.",
# )
 
# ServerErrorException = HTTPException(
#     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#     detail="Something went wrong on our end. Please try again later.",
# )