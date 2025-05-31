package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"loyalty-platform/user-service/models"
	"loyalty-platform/user-service/repository"
)

func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	assert.NoError(t, err)

	err = db.AutoMigrate(&models.User{})
	assert.NoError(t, err)

	return db
}

func setupTestRouter(db *gorm.DB) *gin.Engine {
	gin.SetMode(gin.TestMode)
	router := gin.Default()
	handler := NewUserHandler(db)

	api := router.Group("/api/v1")
	{
		users := api.Group("/users")
		{
			users.POST("", handler.CreateUser)
			users.GET("/:id", handler.GetUser)
			users.PUT("/:id", handler.UpdateUser)
			users.DELETE("/:id", handler.DeleteUser)
		}
	}

	return router
}

func TestCreateUser(t *testing.T) {
	db := setupTestDB(t)
	router := setupTestRouter(db)

	// Test valid user creation
	userReq := models.CreateUserRequest{
		Email:     "test@example.com",
		FirstName: "John",
		LastName:  "Doe",
		Phone:     "1234567890",
		Address:   "123 Test St",
	}

	reqBody, _ := json.Marshal(userReq)
	req := httptest.NewRequest(http.MethodPost, "/api/v1/users", bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)

	var response models.User
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, userReq.Email, response.Email)
	assert.Equal(t, userReq.FirstName, response.FirstName)
	assert.Equal(t, userReq.LastName, response.LastName)
}

func TestGetUser(t *testing.T) {
	db := setupTestDB(t)
	router := setupTestRouter(db)
	repo := repository.NewUserRepository(db)

	// Create a test user
	user := &models.User{
		ID:        uuid.New(),
		Email:     "test@example.com",
		FirstName: "John",
		LastName:  "Doe",
	}
	err := repo.Create(user)
	assert.NoError(t, err)

	// Test getting existing user
	req := httptest.NewRequest(http.MethodGet, "/api/v1/users/"+user.ID.String(), nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response models.User
	err = json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, user.ID, response.ID)
	assert.Equal(t, user.Email, response.Email)

	// Test getting non-existent user
	req = httptest.NewRequest(http.MethodGet, "/api/v1/users/"+uuid.New().String(), nil)
	w = httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
} 