import uvicorn

import duels.api

if __name__ == "__main__":
    uvicorn.run(
        duels.api.app,
        # "duels.api:app",
        port=5000,
        # reload=True,
        access_log=True,
    )
