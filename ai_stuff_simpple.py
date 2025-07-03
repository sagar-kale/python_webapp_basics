# simplified_app.py - Single table with shared servers that multiple users can connect to
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Session, select, create_engine, JSON, Column
from sqlalchemy import DateTime, func, and_
from fastapi import FastAPI, HTTPException, Depends

# ==================== SINGLE TABLE MODEL ====================

class MCPServer(SQLModel, table=True):
    # Auto-generated UUID as primary key
    server_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    
    # Server information (shared across all users)
    name: str = Field(index=True)
    server_type: str  # e.g., "filesystem", "database", "websearch", etc.
    description: Optional[str] = None
    base_config: Dict[str, Any] = Field(sa_column=Column(JSON))  # Base server config
    is_active: bool = Field(default=True)  # Admin can enable/disable servers
    
    # User connection info (NULL if not connected to any user)
    user_id: Optional[str] = Field(default=None, index=True)  # NULL = available, has value = connected
    is_connected: bool = Field(default=False, index=True)
    user_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # User-specific config
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    connected_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

# ==================== API MODELS ====================

class MCPServerCreate(SQLModel):
    name: str
    server_type: str
    description: Optional[str] = None
    base_config: Dict[str, Any]

class MCPServerUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class UserConnectionUpdate(SQLModel):
    user_config: Optional[Dict[str, Any]] = None

class MCPServerRead(SQLModel):
    server_id: str
    name: str
    server_type: str
    description: Optional[str]
    base_config: Dict[str, Any]
    is_active: bool
    user_id: Optional[str]
    is_connected: bool
    user_config: Optional[Dict[str, Any]]
    created_at: datetime
    connected_at: Optional[datetime]
    last_used: Optional[datetime]

class AvailableServerRead(SQLModel):
    """For available servers list (without user-specific info)"""
    server_id: str
    name: str
    server_type: str
    description: Optional[str]
    base_config: Dict[str, Any]
    is_active: bool
    created_at: datetime

class MCPServerListResponse(SQLModel):
    servers: List[MCPServerRead]

class AvailableServerListResponse(SQLModel):
    servers: List[AvailableServerRead]

class ConnectionResponse(SQLModel):
    message: str
    server_id: str

# ==================== DATABASE OPERATIONS ====================

class MCPDatabaseOperations:
    def __init__(self, session: Session):
        self.session = session
    
    def create_server(self, server_data: MCPServerCreate) -> MCPServer:
        """Create a new MCP server (admin function)"""
        server = MCPServer(
            name=server_data.name,
            server_type=server_data.server_type,
            description=server_data.description,
            base_config=server_data.base_config,
            is_active=True,
            user_id=None,  # Available for connection
            is_connected=False
        )
        self.session.add(server)
        self.session.commit()
        self.session.refresh(server)
        return server
    
    def get_available_servers(self) -> List[MCPServer]:
        """Get all active servers that are available for connection"""
        statement = select(MCPServer).where(
            MCPServer.is_active == True,
            MCPServer.user_id.is_(None)
        )
        return self.session.exec(statement).all()
    
    def get_user_servers(self, user_id: str) -> List[MCPServer]:
        """Get all servers connected to a specific user"""
        statement = select(MCPServer).where(MCPServer.user_id == user_id)
        return self.session.exec(statement).all()
    
    def get_connected_servers(self, user_id: str) -> List[MCPServer]:
        """Get only connected servers for a user"""
        statement = select(MCPServer).where(
            MCPServer.user_id == user_id,
            MCPServer.is_connected == True
        )
        return self.session.exec(statement).all()
    
    def get_server_by_id(self, server_id: str) -> Optional[MCPServer]:
        """Get server by ID"""
        statement = select(MCPServer).where(MCPServer.server_id == server_id)
        return self.session.exec(statement).first()
    
    def get_user_server_by_id(self, server_id: str, user_id: str) -> Optional[MCPServer]:
        """Get server by ID that belongs to specific user"""
        statement = select(MCPServer).where(
            MCPServer.server_id == server_id,
            MCPServer.user_id == user_id
        )
        return self.session.exec(statement).first()
    
    def connect_server(self, server_id: str, user_id: str, user_config: Optional[Dict[str, Any]] = None) -> bool:
        """Connect user to an available server"""
        server = self.get_server_by_id(server_id)
        if server and server.is_active and server.user_id is None:
            # Server is available for connection
            server.user_id = user_id
            server.is_connected = True
            server.user_config = user_config
            server.connected_at = datetime.utcnow()
            server.last_used = datetime.utcnow()
            self.session.add(server)
            self.session.commit()
            return True
        return False
    
    def disconnect_server(self, server_id: str, user_id: str) -> bool:
        """Disconnect user from a server"""
        server = self.get_user_server_by_id(server_id, user_id)
        if server:
            server.is_connected = False
            # Note: We keep user_id to maintain "Your Servers" list
            self.session.add(server)
            self.session.commit()
            return True
        return False
    
    def reconnect_server(self, server_id: str, user_id: str) -> bool:
        """Reconnect user to a server they previously connected to"""
        server = self.get_user_server_by_id(server_id, user_id)
        if server and server.is_active:
            server.is_connected = True
            server.connected_at = datetime.utcnow()
            server.last_used = datetime.utcnow()
            self.session.add(server)
            self.session.commit()
            return True
        return False
    
    def update_user_config(self, server_id: str, user_id: str, user_config: Dict[str, Any]) -> bool:
        """Update user-specific configuration for a server"""
        server = self.get_user_server_by_id(server_id, user_id)
        if server:
            server.user_config = user_config
            server.last_used = datetime.utcnow()
            self.session.add(server)
            self.session.commit()
            return True
        return False
    
    def update_server(self, server_id: str, update_data: MCPServerUpdate) -> Optional[MCPServer]:
        """Update server details (admin function)"""
        server = self.get_server_by_id(server_id)
        if server:
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(server, field, value)
            
            self.session.add(server)
            self.session.commit()
            self.session.refresh(server)
            return server
        return None
    
    def delete_server(self, server_id: str) -> bool:
        """Delete a server (admin function)"""
        server = self.get_server_by_id(server_id)
        if server:
            self.session.delete(server)
            self.session.commit()
            return True
        return False
    
    def initialize_sample_servers(self):
        """Initialize sample servers for the platform"""
        # Check if servers already exist
        existing_servers = self.session.exec(select(MCPServer)).first()
        
        if not existing_servers:
            sample_servers = [
                MCPServerCreate(
                    name="File System Server",
                    server_type="filesystem",
                    description="Access and manage files and directories",
                    base_config={"transport": "stdio", "url": "mcp://filesystem"}
                ),
                MCPServerCreate(
                    name="Database Query Server",
                    server_type="database",
                    description="Execute database queries and manage data",
                    base_config={"transport": "stdio", "url": "mcp://database"}
                ),
                MCPServerCreate(
                    name="Web Search Server",
                    server_type="websearch",
                    description="Search the web for information",
                    base_config={"transport": "http", "url": "mcp://websearch"}
                ),
                MCPServerCreate(
                    name="Code Analysis Server",
                    server_type="codeanalysis",
                    description="Analyze and understand code repositories",
                    base_config={"transport": "stdio", "url": "mcp://codeanalysis"}
                ),
                MCPServerCreate(
                    name="Git Operations Server",
                    server_type="git",
                    description="Perform Git operations and version control",
                    base_config={"transport": "stdio", "url": "mcp://git"}
                ),
                MCPServerCreate(
                    name="Terminal Server",
                    server_type="terminal",
                    description="Execute terminal commands",
                    base_config={"transport": "stdio", "url": "mcp://terminal"}
                ),
                MCPServerCreate(
                    name="API Client Server",
                    server_type="apiclient",
                    description="Make HTTP API calls and handle responses",
                    base_config={"transport": "http", "url": "mcp://apiclient"}
                ),
                MCPServerCreate(
                    name="Calendar Server",
                    server_type="calendar",
                    description="Manage calendar events and schedules",
                    base_config={"transport": "http", "url": "mcp://calendar"}
                )
            ]
            
            for server_data in sample_servers:
                self.create_server(server_data)
            
            print(f"Created {len(sample_servers)} sample servers")

# ==================== FASTAPI APPLICATION ====================

# Mock OAuth function - replace with your actual implementation
def get_current_userid() -> str:
    """Replace this with your actual OAuth function"""
    return "user123"

app = FastAPI(title="MCP Server Management API")

# Database setup
DATABASE_URL = "sqlite:///mcp_servers.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Database session dependency"""
    with Session(engine) as session:
        yield session

@app.on_event("startup")
async def startup_event():
    """Initialize database and sample servers"""
    create_db_and_tables()
    
    # Create sample servers
    with Session(engine) as session:
        db_ops = MCPDatabaseOperations(session)
        db_ops.initialize_sample_servers()

# ==================== API ENDPOINTS ====================

@app.get("/api/available-servers")
async def get_available_servers(
    session: Session = Depends(get_session)
):
    """Get all available servers that can be connected to"""
    db_ops = MCPDatabaseOperations(session)
    servers = db_ops.get_available_servers()
    
    available_servers = [
        AvailableServerRead(**server.dict()) 
        for server in servers
    ]
    
    return AvailableServerListResponse(servers=available_servers)

@app.get("/api/your-servers")
async def get_your_servers(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Get all servers this user has ever connected to"""
    db_ops = MCPDatabaseOperations(session)
    servers = db_ops.get_user_servers(user_id)
    
    return MCPServerListResponse(servers=servers)

@app.get("/api/connected-servers")
async def get_connected_servers(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Get servers this user is currently connected to"""
    db_ops = MCPDatabaseOperations(session)
    servers = db_ops.get_connected_servers(user_id)
    
    return MCPServerListResponse(servers=servers)

@app.post("/api/connect-server/{server_id}")
async def connect_server(
    server_id: str,
    connection_data: Optional[UserConnectionUpdate] = None,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Connect to an available server"""
    db_ops = MCPDatabaseOperations(session)
    
    # Check if user already connected to this server
    existing_connection = db_ops.get_user_server_by_id(server_id, user_id)
    if existing_connection:
        # User previously connected, just reconnect
        success = db_ops.reconnect_server(server_id, user_id)
        if success:
            return ConnectionResponse(
                message="Successfully reconnected to server",
                server_id=server_id
            )
        else:
            raise HTTPException(status_code=400, detail="Server is not active")
    
    # First time connection
    user_config = connection_data.user_config if connection_data else None
    success = db_ops.connect_server(server_id, user_id, user_config)
    
    if success:
        return ConnectionResponse(
            message="Successfully connected to server",
            server_id=server_id
        )
    else:
        raise HTTPException(status_code=400, detail="Server not available for connection")

@app.post("/api/disconnect-server/{server_id}")
async def disconnect_server(
    server_id: str,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Disconnect from a server"""
    db_ops = MCPDatabaseOperations(session)
    success = db_ops.disconnect_server(server_id, user_id)
    
    if success:
        return ConnectionResponse(
            message="Successfully disconnected from server",
            server_id=server_id
        )
    else:
        raise HTTPException(status_code=404, detail="Server connection not found")

@app.put("/api/servers/{server_id}/user-config")
async def update_user_config(
    server_id: str,
    config_data: UserConnectionUpdate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Update user-specific configuration for a server"""
    db_ops = MCPDatabaseOperations(session)
    success = db_ops.update_user_config(server_id, user_id, config_data.user_config)
    
    if success:
        return {"message": "User configuration updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Server connection not found")

@app.get("/api/servers/{server_id}")
async def get_server_details(
    server_id: str,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Get server details"""
    db_ops = MCPDatabaseOperations(session)
    
    # Try to get user's connection to this server first
    server = db_ops.get_user_server_by_id(server_id, user_id)
    
    if not server:
        # If user doesn't have connection, get the base server info
        server = db_ops.get_server_by_id(server_id)
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    return MCPServerRead(**server.dict())

# ==================== ADMIN ENDPOINTS ====================

@app.post("/api/admin/servers")
async def create_server(
    server_data: MCPServerCreate,
    session: Session = Depends(get_session)
):
    """Create a new MCP server (admin function)"""
    db_ops = MCPDatabaseOperations(session)
    server = db_ops.create_server(server_data)
    
    return {
        "message": "Server created successfully",
        "server": AvailableServerRead(**server.dict())
    }

@app.put("/api/admin/servers/{server_id}")
async def update_server(
    server_id: str,
    update_data: MCPServerUpdate,
    session: Session = Depends(get_session)
):
    """Update server details (admin function)"""
    db_ops = MCPDatabaseOperations(session)
    server = db_ops.update_server(server_id, update_data)
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    return {
        "message": "Server updated successfully",
        "server": AvailableServerRead(**server.dict())
    }

@app.delete("/api/admin/servers/{server_id}")
async def delete_server(
    server_id: str,
    session: Session = Depends(get_session)
):
    """Delete a server (admin function)"""
    db_ops = MCPDatabaseOperations(session)
    success = db_ops.delete_server(server_id)
    
    if success:
        return {"message": "Server deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Server not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
