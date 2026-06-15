import grpc
from concurrent import futures
import movie_pb2
import movie_pb2_grpc
from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://geekvault:geekvault123@geekvault.cn69hdg.mongodb.net/?appName=GeekVault"
)

db = client["GeekVault"]

movies_collection = db["movies"]


class MovieService(movie_pb2_grpc.MovieServiceServicer):

    def RegisterMovie(self, request, context):
        movies_collection.insert_one({
            "_id": request.id,
            "name": request.name,
            "kind": request.kind,
            "year": request.year,
            "score": request.score
        })
        return movie_pb2.Response(response=str(movies_collection.find_one({"_id": request.id})))
    
    def SearchMovie(self, request, context):
        return movie_pb2.Movie()

    def DeleteMovie(self, request, context):
        return movie_pb2.Response(
        response="Pendiente"
    )

    def UpdateMovie(self, request, context):
        #Buscamos la pelicula por id
        pelicula = movies_collection.find_one({"_id":request.id})

        #Si no existe
        if pelicula is None:
            return movie_pb2.Response(response=f"Error: No se encontró ninguna pelicula con id {request.id}")
        #Si existe actualizamos
        movies_collection.update_one(
            {"_id": request.id},
            {"$set":{
                "name":request.name,
                "kind":request.kind,
                "year":request.year,
                "score":request.score
            }})
        #Confirmmos los datos actulizados
        actulizado = movies_collection.find_one({"_id": request.id})
        return movie_pb2.Response(response=f"Pelicula actualizada: {actulizado}")
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_MovieServiceServicer_to_server(MovieService(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC corriendo en puerto 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()