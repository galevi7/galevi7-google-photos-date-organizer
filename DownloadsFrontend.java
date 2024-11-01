import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
public class DownloadsFrontend {
    public static void main(String[] args) {

        PhotoDownloader downloader = new PhotoDownloader();
        downloader.crawler("https://photos.google.com/photo/AF1QipM9B1DCovcvMJlsR_kLNYIsUCSwuWxH6nlPLoVk",
                "C:\\Users\\galev\\OneDrive\\Desktop\\Google Photos",true, false,
                3, true,"", "");
        String path = downloader.makeDirectory("C:\\Users\\galev\\OneDrive\\Desktop", "Google Photos");
        System.out.println("the path is: " + path);
        downloader.killDriver();
    }
}
