import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class DownloadsFrontend {
    public static void main(String[] args) {
        PhotoDownloader downloader = new PhotoDownloader();
        String path = downloader.makeDirectory("C:\\Users\\galev\\OneDrive\\Desktop", "Google Photos");
        System.out.println("the path is: " + path);
        downloader.killDriver();
    }
}
