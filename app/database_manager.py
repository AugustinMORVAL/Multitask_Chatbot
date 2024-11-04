from typing import Any, Dict
from pymongo import MongoClient
from qdrant_client import QdrantClient
import json
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from datetime import datetime


class DatabaseManager:
    def __init__(self, database_type: str, connection_params: Dict[str, Any]):
        self.database_type = database_type.lower()
        self.connection_params = connection_params
        self.connection = None
        self._validate_connection_params(connection_params)
        
        if self.database_type in ["sqlite", "mysql", "postgresql"]:
            self._manager = SQLDatabaseManager(self.database_type, self.connection_params)
        else:
            self._manager = NoSQLDatabaseManager(self.database_type, self.connection_params)

        self.status = "disconnected"
        self.last_error = None
        self.connection_timestamp = None

    def _validate_connection_params(self, params: Dict[str, Any]) -> None:
        if not params:
            raise ValueError("Connection parameters cannot be empty")
        if self.database_type in ["mysql", "postgresql"]:
            required_params = ["host", "username", "password", "database"]
            missing_params = [param for param in required_params if param not in params]
            if missing_params:
                raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        elif self.database_type == "sqlite":
            if "file_path" not in params and "database" not in params:
                raise ValueError("SQLite requires either file_path or database parameter")
        elif self.database_type == "mongodb":
            if "url" not in params and "host" not in params:
                raise ValueError("MongoDB requires either url or host parameter")
        elif self.database_type == "qdrant":
            if "url" not in params:
                raise ValueError("Qdrant requires url parameter")

    def create_connection(self):
        try:
            manager = self._manager
            manager.connect()
            self.status = "connected"
            self.connection_timestamp = datetime.now()
            self.last_error = None
            return manager
        except Exception as e:
            self.status = "error"
            self.last_error = str(e)
            raise

    @property
    def is_connected(self) -> bool:
        return self._manager.connection is not None

    def get_connection_info(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "type": self.database_type,
            "last_error": self.last_error,
            "connected_since": self.connection_timestamp,
            "is_connected": self.is_connected
        }

    def disconnect(self):
        """Explicitly disconnect from the database."""
        try:
            self._manager.disconnect()
            self.status = "disconnected"
            self.connection_timestamp = None
        except Exception as e:
            self.status = "error"
            self.last_error = str(e)
            raise


class SQLDatabaseManager:
    def __init__(self, database_type: str, connection_params: Dict[str, Any]):
        self.database_type = database_type
        self.connection_params = connection_params
        self.connection = None
        self.engine = None

    def connect(self) -> Any:
        if self.is_connected:
            return self.connection

        try:
            if 'file_path' in self.connection_params:
                connection_string = f"sqlite:///{self.connection_params['file_path']}"
            else:
                url = self.connection_params['url']
                if 'username' in self.connection_params:
                    credentials = f"{self.connection_params['username']}:{self.connection_params['password']}"
                    url = url.replace('://', f"://{credentials}@")
                connection_string = url

            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10
            )
            self.connection = self.engine.connect()

            self.connection = self.engine.connect()
            return self.connection
            
        except Exception as e:
            detailed_error = str(e)
            if "Access denied" in detailed_error:
                raise ConnectionError("Invalid username or password")
            elif "Unknown database" in detailed_error:
                raise ConnectionError("Database does not exist")
            elif "Connection refused" in detailed_error:
                raise ConnectionError("Unable to reach database server. Please check host and port")
            else:
                raise ConnectionError(f"Failed to connect to SQL database: {detailed_error}")

    def query(self, query: str) -> Any:
        if not self.is_connected:
            raise ConnectionError("Database not connected")
        try:
            return self.connection.execute(query)
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
        
    @property
    def is_connected(self) -> bool:
        return self.connection is not None

    def disconnect(self):
        """Explicitly disconnect from the database."""
        if self.connection:
            self.connection.close()
            self.connection = None
        if self.engine:
            self.engine.dispose()
            self.engine = None


class NoSQLDatabaseManager:
    def __init__(self, database_type: str, connection_params: Dict[str, Any]):
        self.database_type = database_type
        self.connection_params = connection_params
        self.connection = None

    def connect(self) -> Any:
        if self.is_connected:
            return self.connection

        try:
            db_type = self.database_type.lower()
            
            if db_type == 'mongodb':
                if 'url' in self.connection_params:
                    self.connection = MongoClient(self.connection_params['url'])
                else:
                    self.connection = MongoClient(
                        host=self.connection_params.get('host', 'localhost'),
                        port=self.connection_params.get('port', 27017),
                        username=self.connection_params.get('username'),
                        password=self.connection_params.get('password')
                    )
            elif db_type == 'qdrant':
                self.connection = QdrantClient(
                    url=self.connection_params.get('url'),
                    api_key=self.connection_params.get('api_key')
                )
            else:
                raise ValueError(f"Unsupported NoSQL database type: {db_type}")
                
            return self.connection
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to NoSQL database: {str(e)}")

    def query(self, query: str) -> Any:
        if not self.is_connected:
            raise ConnectionError("Database not connected")
            
        try:
            # Parse the query string as JSON for NoSQL operations
            query_params = json.loads(query)
            db_type = self.database_type.lower()
            
            if db_type == 'mongodb':
                collection = self.connection[query_params.get('database', 'default')][query_params['collection']]
                operation = query_params['operation']
                
                if operation == 'find':
                    return collection.find(query_params.get('filter', {}))
                elif operation == 'insert':
                    return collection.insert_many(query_params['documents'])
                
            elif db_type == 'qdrant':
                return self.connection.search(
                    collection_name=query_params['collection'],
                    query_vector=query_params['vector'],
                    limit=query_params.get('limit', 10)
                )
                
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    @property
    def is_connected(self) -> bool:
        return self.connection is not None

    def disconnect(self):
        """Explicitly disconnect from the database."""
        if self.connection:
            if self.database_type.lower() == 'mongodb':
                self.connection.close()
            elif self.database_type.lower() == 'qdrant':
                # Qdrant client doesn't require explicit closure
                pass
            self.connection = None