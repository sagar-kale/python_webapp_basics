# complete_app.py - Complete FastAPI application with models and endpoints
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, JSON, Column, Session, select, create_engine
from sqlalchemy import DateTime, func, and_
from fastapi import FastAPI, HTTPException, Depends
import json

# ==================== MODELS ====================

# Base models without relationships (for API responses)
class UserBase(SQLModel):
    user_id: str = Field(unique=True, index=True)
    email: str
    name: str

class MCPServerBase(SQLModel):
    name: str
    server_id: str = Field(unique=True, index=True)  # Unique identifier for the MCP server
    config: Dict[str, Any] = Field(sa_column=Column(JSON))  # Contains name, url, transport
    is_active: bool = True

class UserMCPConnectionBase(SQLModel):
    user_id: str = Field(foreign_key="user.user_id")
    server_id: int = Field(foreign_key="mcpserver.id")
    is_connected: bool = False
    connection_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    connected_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

# Database models with relationships
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    
    # Relationships
    connections: List["UserMCPConnection"] = Relationship(back_populates="user")

class MCPServer(MCPServerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    
    # Relationships
    connections: List["UserMCPConnection"] = Relationship(back_populates="server")

class UserMCPConnection(UserMCPConnectionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    
    # Relationships
    user: User = Relationship(back_populates="connections")
    server: MCPServer = Relationship(back_populates="connections")

# API Response models (without relationships to avoid circular references)
class UserRead(UserBase):
    id: int
    created_at: datetime

class MCPServerRead(MCPServerBase):
    id: int
    created_at: datetime
    is_connected: Optional[bool] = None  # Will be set based on user context

class UserMCPConnectionRead(UserMCPConnectionBase):
    id: int
    created_at: datetime
    # Include server details for convenience
    server_name: Optional[str] = None
    server_config: Optional[Dict[str, Any]] = None

# Create/Update models
class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None

class MCPServerCreate(MCPServerBase):
    pass

class MCPServerUpdate(SQLModel):
    name: Optional[str] = None
    server_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class UserMCPConnectionCreate(SQLModel):
    server_id: int
    connection_config: Optional[Dict[str, Any]] = None

class UserMCPConnectionUpdate(SQLModel):
    is_connected: Optional[bool] = None
    connection_config: Optional[Dict[str, Any]] = None
    last_used: Optional[datetime] = None

# Response models for API endpoints
class MCPServerListResponse(SQLModel):
    servers: List[MCPServerRead]

class UserConnectionsResponse(SQLModel):
    connections: List[UserMCPConnectionRead]

class ConnectionResponse(SQLModel):
    message: str
    server_id: int
    connection_id: Optional[int] = None

# Database initialization and sample data
def create_sample_mcp_servers():
    """Sample MCP servers to insert into database"""
    return [
        MCPServerCreate(
            name="File System Server",
            server_id="filesystem",
            config={
                "name": "File System",
                "url": "mcp://filesystem",
                "transport": "stdio"
            }
        ),
        MCPServerCreate(
            name="Database Query Server",
            server_id="database",
            config={
                "name": "Database Query",
                "url": "mcp://database",
                "transport": "stdio"
            }
        ),
        MCPServerCreate(
            name="Web Search Server",
            server_id="websearch",
            config={
                "name": "Web Search",
                "url": "mcp://websearch",
                "transport": "http"
            }
        ),
        MCPServerCreate(
            name="Code Analysis Server",
            server_id="codeanalysis",
            config={
                "name": "Code Analysis",
                "url": "mcp://codeanalysis",
                "transport": "stdio"
            }
        ),
        MCPServerCreate(
            name="Git Operations Server",
            server_id="git",
            config={
                "name": "Git Operations",
                "url": "mcp://git",
                "transport": "stdio"
            }
        ),
        MCPServerCreate(
            name="API Client Server",
            server_id="apiclient",
            config={
                "name": "API Client",
                "url": "mcp://apiclient",
                "transport": "http"
            }
        ),
        MCPServerCreate(
            name="Terminal Server",
            server_id="terminal",
            config={
                "name": "Terminal",
                "url": "mcp://terminal",
                "transport": "stdio"
            }
        ),
        MCPServerCreate(
            name="Calendar Server",
            server_id="calendar",
            config={
                "name": "Calendar",
                "url": "mcp://calendar",
                "transport": "http"
            }
        )
    ]

# Database operations class
class MCPDatabaseOperations:
    def __init__(self, session: Session):
        self.session = session
    
    def create_or_update_user(self, user_data: UserCreate) -> User:
        """Create or update user from OAuth data"""
        # Check if user exists
        statement = select(User).where(User.user_id == user_data.user_id)
        existing_user = self.session.exec(statement).first()
        
        if existing_user:
            # Update existing user
            existing_user.email = user_data.email
            existing_user.name = user_data.name
            self.session.add(existing_user)
            self.session.commit()
            self.session.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            user = User(**user_data.dict())
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
    
    def get_available_mcp_servers(self) -> List[MCPServer]:
        """Get all active MCP servers"""
        statement = select(MCPServer).where(MCPServer.is_active == True)
        return self.session.exec(statement).all()
    
    def get_user_connections(self, user_id: str) -> List[UserMCPConnectionRead]:
        """Get user's MCP connections with server details"""
        statement = select(
            UserMCPConnection,
            MCPServer.name,
            MCPServer.config
        ).join(MCPServer).where(UserMCPConnection.user_id == user_id)
        
        results = self.session.exec(statement).all()
        
        connections = []
        for connection, server_name, server_config in results:
            conn_data = UserMCPConnectionRead(
                **connection.dict(),
                server_name=server_name,
                server_config=server_config
            )
            connections.append(conn_data)
        
        return connections
    
    def get_servers_with_user_status(self, user_id: str) -> List[MCPServerRead]:
        """Get all servers with connection status for specific user"""
        # Get all servers
        servers = self.get_available_mcp_servers()
        
        # Get user's connected server IDs
        statement = select(UserMCPConnection.server_id).where(
            and_(
                UserMCPConnection.user_id == user_id,
                UserMCPConnection.is_connected == True
            )
        )
        connected_server_ids = set(self.session.exec(statement).all())
        
        # Add connection status to servers
        server_reads = []
        for server in servers:
            server_read = MCPServerRead(
                **server.dict(),
                is_connected=server.id in connected_server_ids
            )
            server_reads.append(server_read)
        
        return server_reads
    
    def connect_user_to_server(self, user_id: str, server_id: int, config: Optional[Dict] = None) -> UserMCPConnection:
        """Connect user to MCP server"""
        # Check if connection already exists
        statement = select(UserMCPConnection).where(
            and_(
                UserMCPConnection.user_id == user_id,
                UserMCPConnection.server_id == server_id
            )
        )
        existing_connection = self.session.exec(statement).first()
        
        current_time = datetime.utcnow()
        
        if existing_connection:
            # Update existing connection
            existing_connection.is_connected = True
            existing_connection.connection_config = config
            existing_connection.connected_at = current_time
            existing_connection.last_used = current_time
            self.session.add(existing_connection)
            self.session.commit()
            self.session.refresh(existing_connection)
            return existing_connection
        else:
            # Create new connection
            connection = UserMCPConnection(
                user_id=user_id,
                server_id=server_id,
                is_connected=True,
                connection_config=config,
                connected_at=current_time,
                last_used=current_time
            )
            self.session.add(connection)
            self.session.commit()
            self.session.refresh(connection)
            return connection
    
    def disconnect_user_from_server(self, user_id: str, server_id: int) -> bool:
        """Disconnect user from MCP server"""
        statement = select(UserMCPConnection).where(
            and_(
                UserMCPConnection.user_id == user_id,
                UserMCPConnection.server_id == server_id
            )
        )
        connection = self.session.exec(statement).first()
        
        if connection:
            connection.is_connected = False
            self.session.add(connection)
            self.session.commit()
            return True
        return False
    
    def update_connection_config(self, user_id: str, server_id: int, config: Dict) -> bool:
        """Update connection configuration"""
        statement = select(UserMCPConnection).where(
            and_(
                UserMCPConnection.user_id == user_id,
                UserMCPConnection.server_id == server_id
            )
        )
        connection = self.session.exec(statement).first()
        
        if connection:
            connection.connection_config = config
            connection.last_used = datetime.utcnow()
            self.session.add(connection)
            self.session.commit()
            return True
        return False
    
    def get_server_by_id(self, server_id: int) -> Optional[MCPServer]:
        """Get server by ID"""
        statement = select(MCPServer).where(MCPServer.id == server_id)
        return self.session.exec(statement).first()
    
    def create_mcp_server(self, server_data: MCPServerCreate) -> MCPServer:
        """Create new MCP server"""
        server = MCPServer(**server_data.dict())
        self.session.add(server)
        self.session.commit()
        self.session.refresh(server)
        return server
    
    def initialize_sample_servers(self):
        """Initialize database with sample MCP servers"""
        # Check if servers already exist
        statement = select(MCPServer)
        existing_servers = self.session.exec(statement).first()
        
        if not existing_servers:
            # Create sample servers
            sample_servers = create_sample_mcp_servers()
            for server_data in sample_servers:
                server = MCPServer(**server_data.dict())
                self.session.add(server)
            
            self.session.commit()
            print("Sample MCP servers created successfully!")
        else:
            print("MCP servers already exist in database.")

# ==================== FASTAPI APPLICATION ====================

# Import your OAuth function here
# from your_oauth_lib import get_current_userid

# Mock function for demonstration - replace with your actual OAuth function
def get_current_userid() -> str:
    """Replace this with your actual OAuth function"""
    # This is a placeholder - replace with your actual implementation
    return "user123"  # This should come from your OAuth library

app = FastAPI(title="MCP Server Management API")

# Database setup
DATABASE_URL = "sqlite:///app.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Database session dependency"""
    with Session(engine) as session:
        yield session

def ensure_user_exists(user_id: str, session: Session) -> User:
    """Ensure user exists in database, create if not"""
    db_ops = MCPDatabaseOperations(session)
    
    # Create user with just user_id since name/email aren't available yet
    user_create = UserCreate(
        user_id=user_id,
        email='',  # Empty for now
        name=user_id  # Use user_id as name for now
    )
    
    return db_ops.create_or_update_user(user_create)

def get_db_user(user_id: str, session: Session) -> User:
    """Get user from database, create if doesn't exist"""
    statement = select(User).where(User.user_id == user_id)
    db_user = session.exec(statement).first()
    
    if not db_user:
        # Auto-create user if they don't exist
        db_user = ensure_user_exists(user_id, session)
    
    return db_user

@app.on_event("startup")
async def startup_event():
    """Initialize database and sample data"""
    create_db_and_tables()
    
    # Create sample servers
    with Session(engine) as session:
        db_ops = MCPDatabaseOperations(session)
        db_ops.initialize_sample_servers()

@app.get("/api/mcp-servers")
async def get_mcp_servers(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Get all available MCP servers with user connection status"""
    # Ensure user exists in database
    get_db_user(user_id, session)
    
    db_ops = MCPDatabaseOperations(session)
    servers = db_ops.get_servers_with_user_status(user_id)
    
    return MCPServerListResponse(servers=servers)

@app.post("/api/connect-mcp-server/{server_id}")
async def connect_to_mcp_server(
    server_id: int,
    connection_data: Optional[UserMCPConnectionCreate] = None,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Connect user to an MCP server"""
    try:
        # Ensure user exists in database
        get_db_user(user_id, session)
        
        db_ops = MCPDatabaseOperations(session)
        
        # Verify server exists
        server = db_ops.get_server_by_id(server_id)
        if not server:
            raise HTTPException(status_code=404, detail="MCP server not found")
        
        # Create connection
        config = connection_data.connection_config if connection_data else None
        connection = db_ops.connect_user_to_server(
            user_id=user_id,
            server_id=server_id,
            config=config
        )
        
        return ConnectionResponse(
            message="Successfully connected to MCP server",
            server_id=server_id,
            connection_id=connection.id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to MCP server: {str(e)}")

@app.post("/api/disconnect-mcp-server/{server_id}")
async def disconnect_from_mcp_server(
    server_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Disconnect user from an MCP server"""
    # Ensure user exists in database
    get_db_user(user_id, session)
    
    db_ops = MCPDatabaseOperations(session)
    success = db_ops.disconnect_user_from_server(
        user_id=user_id,
        server_id=server_id
    )
    
    if success:
        return ConnectionResponse(
            message="Successfully disconnected from MCP server",
            server_id=server_id
        )
    else:
        raise HTTPException(status_code=404, detail="Connection not found")

@app.get("/api/my-connections")
async def get_my_connections(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Get user's MCP server connections"""
    # Ensure user exists in database
    get_db_user(user_id, session)
    
    db_ops = MCPDatabaseOperations(session)
    connections = db_ops.get_user_connections(user_id)
    
    return UserConnectionsResponse(connections=connections)

@app.put("/api/update-connection-config/{server_id}")
async def update_connection_config(
    server_id: int,
    config: Dict,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Update connection configuration for a specific MCP server"""
    # Ensure user exists in database
    get_db_user(user_id, session)
    
    db_ops = MCPDatabaseOperations(session)
    success = db_ops.update_connection_config(
        user_id=user_id,
        server_id=server_id,
        config=config
    )
    
    if success:
        return {"message": "Configuration updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Connection not found")

@app.put("/api/update-profile")
async def update_user_profile(
    profile_data: UserCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Update user profile information"""
    db_ops = MCPDatabaseOperations(session)
    
    # Update the user profile
    profile_data.user_id = user_id  # Ensure user_id matches
    updated_user = db_ops.create_or_update_user(profile_data)
    
    return {"message": "Profile updated successfully", "user": updated_user}

@app.get("/api/server-details/{server_id}")
async def get_server_details(
    server_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Get detailed information about a specific MCP server"""
    # Ensure user exists in database
    get_db_user(user_id, session)
    
    db_ops = MCPDatabaseOperations(session)
    server = db_ops.get_server_by_id(server_id)
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    return MCPServerRead(**server.dict())

@app.post("/api/create-mcp-server")
async def create_mcp_server(
    server_data: MCPServerCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_userid)
):
    """Create a new MCP server (admin functionality)"""
    # Ensure user exists in database
    get_db_user(user_id, session)
    
    db_ops = MCPDatabaseOperations(session)
    server = db_ops.create_mcp_server(server_data)
    
    return {"message": "MCP server created successfully", "server": server}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
