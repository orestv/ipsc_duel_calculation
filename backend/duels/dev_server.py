import uvicorn

import duels.api

if __name__ == "__main__":
    uvicorn.run(
        duels.api.app,
        # "duels.api:app",
        host="0.0.0.0",
        port=4200,
        # reload=True,
        access_log=True,
    )
