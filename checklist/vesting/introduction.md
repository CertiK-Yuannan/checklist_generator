This vesting contract is designed to lock and release assets (both native currency and ERC-20 tokens) to a specified beneficiary according to a predefined vesting schedule.

### Key Actors
- Admin: The deployer or the current owner of the contract, who can transfer ownership to a new beneficiary.
- Beneficiary (User): The recipient of the vested assets, who can claim or release the vested amounts.

### Key Modules
1. Schedule Creation
- Admin sets up the vesting schedule by specifying the start time and duration when deploying the contract.
- The schedule is immutable after deployment.
2. Claim/Release
- The beneficiary can release vested assets (either ETH or ERC-20 tokens) at any time.
- The contract calculates the releasable amount using a linear vesting curve.
3. Revoke
- Admin/User can cancel the user's vesting schedule.